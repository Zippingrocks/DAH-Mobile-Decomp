package javax.microedition.media;
import java.io.*;
import java.util.*;
/** Scripted TEST DOUBLE ONLY. Logs API use; never decodes or plays sound.
 * One-shot faults avoid concealing the original's recursive stop-error behavior.
 */
public final class Manager {
    public static final List<String> calls = new ArrayList<String>();
    public static final List<FakePlayer> players = new ArrayList<FakePlayer>();
    public static int faultPoint, faultMode, remaining, createdState, prefetchedState;
    public static boolean returnNull;
    public static void reset() {
        calls.clear(); players.clear(); faultPoint = faultMode = remaining = 0;
        createdState = 100; prefetchedState = 300; returnNull = false;
    }
    private static void hit(int point) throws MediaException {
        if (point != faultPoint || remaining == 0) return;
        --remaining;
        if (faultMode == 1) throw new IllegalStateException("scripted");
        if (faultMode == 2) throw new MediaException("scripted");
        if (faultMode == 3) throw new IllegalArgumentException("scripted");
        if (faultMode == 4) throw new AssertionError("scripted");
    }
    private static void unchecked(int point) {
        try { hit(point); } catch (MediaException ex) { throw new IllegalStateException("scripted"); }
    }
    public static Player createPlayer(InputStream stream, String type) throws IOException, MediaException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        int next;
        while ((next = stream.read()) != -1) out.write(next);
        calls.add("create:" + type + ":" + Arrays.toString(out.toByteArray()));
        if (faultPoint == 1 && remaining > 0 && faultMode == 5) {
            --remaining; throw new IOException("scripted");
        }
        hit(1);
        if (returnNull) return null;
        FakePlayer player = new FakePlayer(players.size(), createdState);
        players.add(player);
        return player;
    }
    public static final class FakePlayer implements Player {
        public final int id;
        public int state, loops;
        public long time = -1;
        public PlayerListener listener;
        FakePlayer(int id, int state) { this.id = id; this.state = state; }
        private void log(String event) { calls.add(id + ":" + event); }
        public void addPlayerListener(PlayerListener value) { log("listener"); unchecked(2); listener = value; }
        public void realize() throws MediaException { log("realize"); hit(3); state = 200; }
        public void prefetch() throws MediaException { log("prefetch"); hit(4); state = prefetchedState; }
        public int getState() { log("state=" + state); unchecked(5); return state; }
        public void setLoopCount(int value) { log("loop=" + value); unchecked(6); loops = value; }
        public void start() throws MediaException { log("start"); hit(7); state = 400; }
        public void stop() throws MediaException { log("stop"); hit(8); state = 300; }
        public long setMediaTime(long value) throws MediaException { log("time=" + value); hit(9); time = value; return value; }
    }
}
