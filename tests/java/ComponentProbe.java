import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.lang.reflect.Array;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Random;
import javax.microedition.lcdui.Image;

/**
 * Differential component probe, not a game runner. Run separately on original
 * and recovered e/s/t classes with the SAME authored Image and o test doubles.
 * No expected gameplay is implemented here. Outcomes are compared by the runner.
 * Exceptions are compared by type, not diagnostic message or stack-trace text.
 */
public final class ComponentProbe {
    private static final Class<?> E = load("e");
    private static final Class<?> S = load("s");
    private static final Class<?> T = load("t");
    private static MessageDigest digest;
    private static long calls;
    private static boolean candidate;

    private static Class<?> load(String name) {
        try { return Class.forName(name); }
        catch (Exception ex) { throw new AssertionError(ex); }
    }

    private static void begin() throws Exception {
        digest = MessageDigest.getInstance("SHA-256");
        calls = 0;
    }

    private static void emit(Object value) {
        if (value == null) { word("null"); return; }
        if (value instanceof Image) { word("image:" + ((Image) value).path); return; }
        if (value.getClass().isArray()) {
            word(value.getClass().getName() + ":" + Array.getLength(value));
            for (int i = 0; i < Array.getLength(value); ++i) emit(Array.get(value, i));
            return;
        }
        word(value.getClass().getName() + ":" + String.valueOf(value));
    }

    private static void word(String value) {
        digest.update(value.getBytes(StandardCharsets.UTF_8));
        digest.update((byte) 0);
    }

    private static void finish(String group) {
        StringBuilder hex = new StringBuilder();
        for (byte b : digest.digest()) hex.append(String.format("%02x", b & 255));
        System.out.println(group + "\t" + calls + "\t" + hex);
    }

    private static Method method(Class<?> owner, String name, Class<?>... types) throws Exception {
        Method result = owner.getDeclaredMethod(name, types);
        result.setAccessible(true);
        return result;
    }

    private static Object call(Method method, Object... args) throws Exception {
        ++calls;
        try {
            Object result = method.invoke(null, args);
            word("return"); emit(result); return result;
        } catch (InvocationTargetException ex) {
            word("throw"); word(ex.getCause().getClass().getName()); return null;
        }
    }

    private static Field field(Class<?> owner, String original, String renamed, Class<?> type) throws Exception {
        String name = candidate ? renamed : original;
        for (Field f : owner.getDeclaredFields()) {
            if (f.getName().equals(name) && f.getType() == type) {
                f.setAccessible(true); return f;
            }
        }
        throw new NoSuchFieldException(owner.getName() + "." + name + ":" + type.getName());
    }

    private static void decoderState(byte header, boolean second) throws Exception {
        field(E, "a", "packedHeader", byte.class).setByte(null, header);
        field(E, "a", "secondPackedValue", boolean.class).setBoolean(null, second);
    }

    private static void recordDecoderState() throws Exception {
        emit(field(E, "a", "packedHeader", byte.class).get(null));
        emit(field(E, "a", "secondPackedValue", boolean.class).get(null));
    }

    private static void constructors() throws Exception {
        begin();
        Constructor<?> ctor = T.getDeclaredConstructor(int.class, int.class, int.class, int.class);
        ctor.setAccessible(true);
        Random r = new Random(0x44544831L);
        int[] edges = {0, 1, -1, Integer.MIN_VALUE, Integer.MAX_VALUE, 32767, -32768, 65536};
        for (int n = 0; n < 5008; ++n) {
            int x = n < edges.length ? edges[n] : r.nextInt();
            Object value = ctor.newInstance(x, ~x, x << 16, x ^ 0x5a5a5a5a);
            ++calls;
            for (String name : new String[]{"a", "b", "c", "d"}) {
                Field f = T.getDeclaredField(name); f.setAccessible(true); emit(f.getInt(value));
            }
        }
        Constructor<?> ec = E.getDeclaredConstructor(); ec.setAccessible(true); ec.newInstance();
        Constructor<?> sc = S.getDeclaredConstructor(); sc.setAccessible(true); sc.newInstance();
        calls += 2;
        for (String name : new String[]{"a", "b", "c"}) emit(field(E, name, name, int.class).get(null));
        recordDecoderState();
        finish("constructors-and-initial-state");
    }

    private static void math() throws Exception {
        begin();
        Method multiply = method(E, "a", long.class, long.class);
        Method divide = method(E, "b", long.class, long.class);
        Method toInt = method(E, "a", int.class);
        Method toFixed = method(E, "b", int.class);
        Method root = method(E, "c", int.class);
        Method distance = method(E, "a", int.class, int.class, int.class, int.class);
        Method scale = method(E, "b", int.class, int.class, int.class, int.class);
        long[] edges = {Long.MIN_VALUE, Long.MAX_VALUE, Integer.MIN_VALUE, Integer.MAX_VALUE,
                -65537, -65536, -32768, -1, 0, 1, 2, 32767, 65535, 65536, 65537};
        for (long x : edges) for (long y : edges) {
            call(multiply, x, y); call(divide, x, y);
        }
        Random r = new Random(0x1122334455667788L);
        for (int n = 0; n < 16000; ++n) {
            long x = r.nextLong(), y = r.nextLong();
            if (n % 17 == 0) y = 0;
            if (n % 19 == 0) y = -1;
            call(multiply, x, y); call(divide, x, y);
            call(toInt, (int) x); call(toFixed, (int) x); call(root, (int) x);
            int a = r.nextInt(), b = r.nextInt(), c = r.nextInt(), d = r.nextInt();
            call(distance, a, b, c, d); call(scale, a, b, n % 11 == 0 ? 0 : c, d);
        }
        for (int x = -32; x < 10000; ++x) call(root, x);
        finish("arithmetic");
    }

    private static void packed() throws Exception {
        begin();
        Method decode = method(E, "a", DataInputStream.class);
        for (int header = 0; header < 256; ++header) for (int low = 0; low < 256; ++low) {
            decoderState((byte) 0, false);
            DataInputStream in = new DataInputStream(new ByteArrayInputStream(
                    new byte[]{(byte) header, (byte) low, (byte) (low * 73 + header)}));
            call(decode, in); recordDecoderState();
            call(decode, in); recordDecoderState();
            emit(in.available());
        }
        for (int state = 0; state < 2; ++state) for (int length = 0; length <= 3; ++length) {
            decoderState((byte) 0xa5, state == 1);
            byte[] bytes = new byte[length];
            for (int i = 0; i < length; ++i) bytes[i] = (byte) (0x82 + i);
            DataInputStream in = new DataInputStream(new ByteArrayInputStream(bytes));
            for (int n = 0; n < 4; ++n) { call(decode, in); recordDecoderState(); }
            // A new stream must not implicitly reset global nibble state.
            call(decode, new DataInputStream(new ByteArrayInputStream(new byte[]{0x56, 0x12, 0x34})));
            recordDecoderState();
        }
        for (int state = 0; state < 2; ++state) {
            decoderState((byte) 0xa5, state == 1);
            call(decode, (Object) null); recordDecoderState();
        }
        finish("packed-reader-and-failures");
    }

    private static void imagePaths() throws Exception {
        begin();
        Method image = method(E, "a", String.class);
        String[] names = {"fixture", "", "/fixture", "a.b", "/fixture.png", "path.with.dot/name", null};
        for (String name : names) for (int mode = 0; mode < 4; ++mode) for (int nulls = 0; nulls < 3; ++nulls) {
            Image.reset(nulls, mode);
            call(image, name);
            emit(Image.calls.toArray(new String[0]));
        }
        finish("image-call-contract-with-test-double");
    }

    private static void rectangles() throws Exception {
        begin();
        Method overlap = method(E, "a", int.class, int.class, int.class, int.class,
                int.class, int.class, int.class, int.class);
        int[][] fixed = {{0, 0, 10, 10, 10, 10, 20, 20}, {0, 0, 10, 10, 11, 0, 20, 10},
                {0, 0, 0, 0, 0, 0, 0, 0}, {10, 10, 0, 0, 1, 1, 2, 2},
                {Integer.MIN_VALUE, -1, Integer.MAX_VALUE, 1, 0, -1, 0, 1}};
        for (int[] row : fixed) {
            Object[] args = new Object[8]; for (int i = 0; i < 8; ++i) args[i] = row[i];
            call(overlap, args);
        }
        Random r = new Random(0x135792468L);
        for (int n = 0; n < 20000; ++n) {
            Object[] args = new Object[8];
            for (int i = 0; i < 8; ++i) args[i] = n < 10000 ? r.nextInt(21) - 10 : r.nextInt();
            call(overlap, args);
        }
        Class<?> O = load("o");
        Method entities = method(E, "a", O, O, int.class);
        byte[] widths = new byte[127], heights = new byte[127];
        for (int i = 0; i < 127; ++i) { widths[i] = (byte) r.nextInt(); heights[i] = (byte) r.nextInt(); }
        field(S, "b", "b", byte[].class).set(null, widths);
        field(S, "c", "c", byte[].class).set(null, heights);
        for (int n = 0; n < 16000; ++n) {
            Object x = O.getDeclaredConstructor().newInstance(), y = O.getDeclaredConstructor().newInstance();
            O.getField("k").setInt(x, r.nextInt()); O.getField("l").setInt(x, r.nextInt());
            O.getField("k").setInt(y, r.nextInt()); O.getField("l").setInt(y, r.nextInt());
            O.getField("q").setByte(x, (byte) (n % 31 == 0 ? -1 : r.nextInt(127)));
            O.getField("q").setByte(y, (byte) (n % 37 == 0 ? 127 : r.nextInt(127)));
            call(entities, x, y, r.nextInt());
        }
        call(entities, null, O.getDeclaredConstructor().newInstance(), 0);
        call(entities, O.getDeclaredConstructor().newInstance(), null, 0);
        finish("inclusive-geometry-with-test-records");
    }

    private static void tableState() throws Exception {
        emit(field(S, "a", "imageNames", String[].class).get(null));
        emit(field(S, "a", "images", Image[].class).get(null));
        emit(field(S, "a", "a", byte[].class).get(null));
        emit(field(S, "a", "offsetX", short[].class).get(null));
        emit(field(S, "b", "offsetY", short[].class).get(null));
        for (String name : new String[]{"b", "c", "d"}) emit(field(S, name, name, byte[].class).get(null));
        emit(field(S, "e", "factorY", byte[].class).get(null));
        recordDecoderState();
    }

    private static void tables() throws Exception {
        begin();
        Method load = method(S, "a", Class.class), get = method(S, "a", byte.class), gc = method(S, "a");
        decoderState((byte) 0, false);
        Image.reset(0, 0);
        tableState();
        call(load, ComponentProbe.class);
        tableState();
        emit(Image.calls.toArray(new String[0]));
        for (int index = -128; index < 128; ++index) call(get, (byte) index);
        tableState();
        emit(Image.calls.toArray(new String[0]));
        // Repeat without resetting state, including after a truncated resource.
        call(load, ComponentProbe.class); tableState();
        call(load, (Object) null); tableState();
        call(gc); tableState();
        finish("object-table-load-cache-and-failures");
    }

    public static void main(String[] args) throws Exception {
        candidate = args[0].equals("candidate");
        if (args.length > 1 && args[1].equals("tables")) {
            tables();
        } else {
            constructors(); math(); packed(); imagePaths(); rectangles();
        }
    }
}
