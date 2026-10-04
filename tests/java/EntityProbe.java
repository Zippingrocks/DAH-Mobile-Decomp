import java.io.*;
import java.lang.reflect.*;
import java.security.MessageDigest;
import java.util.*;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.media.Manager;

/** Independently authored differential tests, NOT a replacement game.
 * Reflection keeps original and source-renamed member identities explicit.
 * Only the target-side JAR is on the process classpath. No fallback loading.
 */
public final class EntityProbe {
    static boolean candidate;
    static final Map<String,String> aliases = new HashMap<String,String>();
    static final Map<String,Field> fields = new HashMap<String,Field>();
    static final Map<String,Method> methods = new HashMap<String,Method>();
    static MessageDigest digest;
    static long calls, successes, failures, fixtureCalls;
    static final Set<String> TARGETS = new HashSet<String>(Arrays.asList("a","o","h","i","m"));
    static final TreeMap<String,long[]> outcomes = new TreeMap<String,long[]>();
    static void track(String owner,String member,String descriptor,boolean success) {
        if(!TARGETS.contains(owner)) return;
        String key=owner+"."+member+descriptor;
        if(!outcomes.containsKey(key))outcomes.put(key,new long[2]);
        outcomes.get(key)[success?0:1]++;
    }
    static final int[] EDGE = {Integer.MIN_VALUE,-65536,-129,-128,-1,0,1,7,100,127,128,65535,Integer.MAX_VALUE};

    static Class<?> C(String name) throws Exception { return Class.forName(name); }
    static String desc(Class<?> c) {
        if(c.isArray()) return c.getName().replace('.','/');
        if(!c.isPrimitive()) return "L"+c.getName().replace('.','/')+";";
        if(c==int.class)return "I"; if(c==byte.class)return "B"; if(c==short.class)return "S";
        if(c==boolean.class)return "Z";if(c==long.class)return "J";if(c==char.class)return "C";
        if(c==float.class)return "F";if(c==double.class)return "D";return "V";
    }
    static String md(Method m) {
        StringBuilder s=new StringBuilder("(");for(Class<?> c:m.getParameterTypes())s.append(desc(c));
        return s.append(')').append(desc(m.getReturnType())).toString();
    }
    static String alias(String kind,String owner,String name,String d) {
        String result=aliases.get(kind+"\t"+owner+"\t"+name+"\t"+d);
        return candidate && result!=null ? result : name;
    }
    static Field F(String owner,String name,String d) throws Exception {
        String key=owner+"#"+name+"#"+d;
        if(!fields.containsKey(key)) {
            String wanted=alias("field",owner,name,d);Field selected=null;
            for(Field f:C(owner).getDeclaredFields())if(f.getName().equals(wanted)&&desc(f.getType()).equals(d))selected=f;
            if(selected==null)throw new AssertionError("Missing field "+key);
            selected.setAccessible(true);fields.put(key,selected);
        }
        return fields.get(key);
    }
    static Object get(String c,Object o,String n,String d)throws Exception{return F(c,n,d).get(o);}
    static void set(String c,Object o,String n,String d,Object v)throws Exception{F(c,n,d).set(o,v);}
    static Method M(String c,String n,String d)throws Exception {
        String key=c+"#"+n+d;
        if(!methods.containsKey(key)) {
            String wanted=alias("method",c,n,d);Method found=null;
            for(Method m:C(c).getDeclaredMethods())if(m.getName().equals(wanted)&&md(m).equals(d))found=m;
            if(found==null)throw new AssertionError("Missing method "+key);
            found.setAccessible(true);methods.put(key,found);
        }
        return methods.get(key);
    }
    static Object invoke(String c,Object o,String n,String d,Object... args)throws Exception {
        if(TARGETS.contains(c))++calls;else ++fixtureCalls;
        try {Object v=M(c,n,d).invoke(o,args);++successes;track(c,n,d,true);add("ok:"+c+"."+n+d+":"+value(v,0));return v;}
        catch(InvocationTargetException e){Throwable t=e.getCause();
            if(t instanceof LinkageError)throw new AssertionError("Broken test linkage",t);
            ++failures;track(c,n,d,false);add("throw:"+c+"."+n+d+":"+t.getClass().getName());return t;
        }
    }
    static Object make(String c,Class<?>[] types,Object...args)throws Exception {
        if(TARGETS.contains(c))++calls;else ++fixtureCalls;
        StringBuilder cd=new StringBuilder("(");for(Class<?> t:types)cd.append(desc(t));cd.append(")V");
        try {Constructor<?> ct=C(c).getDeclaredConstructor(types);ct.setAccessible(true);Object v=ct.newInstance(args);++successes;track(c,"<init>",cd.toString(),true);add("new:"+c);return v;}
        catch(InvocationTargetException e){Throwable t=e.getCause();
            if(t instanceof LinkageError)throw new AssertionError("Broken constructor linkage",t);
            ++failures;track(c,"<init>",cd.toString(),false);add("constructor-throw:"+c+":"+t.getClass().getName());return t;
        }
    }
    static Object xyz(String c,int x,int y,int id)throws Exception{return make(c,new Class<?>[]{int.class,int.class,int.class},x,y,id);}
    static void ok(Object v) {if(v instanceof Throwable)throw new AssertionError("Unexpected fixture failure",(Throwable)v);}
    static void add(String s)throws Exception {byte[] b=s.getBytes("UTF-8");digest.update((byte)(b.length>>>24));digest.update((byte)(b.length>>>16));digest.update((byte)(b.length>>>8));digest.update((byte)b.length);digest.update(b);}
    static String originalField(Field f)throws Exception {
        if(candidate)for(Map.Entry<String,String> entry:aliases.entrySet()) {
            String[] p=entry.getKey().split("\t");
            if(p[0].equals("field")&&p[1].equals(f.getDeclaringClass().getName())&&p[3].equals(desc(f.getType()))&&entry.getValue().equals(f.getName()))return p[2];
        }
        return f.getName();
    }
    static String value(Object v,int depth)throws Exception {
        if(v==null)return "null";
        if(v instanceof Throwable)return "exception:"+v.getClass().getName();
        if(v instanceof Number||v instanceof Boolean||v instanceof Character||v instanceof String)return String.valueOf(v);
        if(v instanceof Image)return "image:"+((Image)v).path;
        if(depth>5)return "ref:"+v.getClass().getName();
        if(v.getClass().isArray()) {StringBuilder s=new StringBuilder("[");for(int n=0;n<Array.getLength(v);++n)s.append(value(Array.get(v,n),depth+1)).append(',');return s.append(']').toString();}
        if(v instanceof Vector){StringBuilder s=new StringBuilder("vector[");for(Object item:(Vector)v)s.append(value(item,depth+1)).append(';');return s.append(']').toString();}
        if(v.getClass().getName().equals("t")||v.getClass().getName().equals("a"))return state(v,depth+1);
        return "ref:"+v.getClass().getName();
    }
    static String state(Object v,int depth)throws Exception {
        if(v==null||v instanceof Throwable)return value(v,depth);
        TreeMap<String,String> result=new TreeMap<String,String>();
        for(Class<?> c=v.getClass();c!=Object.class;c=c.getSuperclass())for(Field f:c.getDeclaredFields()) {
            if(Modifier.isStatic(f.getModifiers()))continue;
            f.setAccessible(true);result.put(c.getName()+"#"+originalField(f)+":"+desc(f.getType()),value(f.get(v),depth+1));
        }
        return v.getClass().getName()+result.toString();
    }
    static void record(Object v)throws Exception {add(state(v,0));}
    static void statics(String c)throws Exception {
        TreeMap<String,String> s=new TreeMap<String,String>();for(Field f:C(c).getDeclaredFields())if(Modifier.isStatic(f.getModifiers())) {
            f.setAccessible(true);s.put(originalField(f)+":"+desc(f.getType()),value(f.get(null),0));
        } add(c+s.toString());
    }
    static void decoder(boolean second)throws Exception {set("e",null,"a","B",(byte)0x9a);set("e",null,"a","Z",second);}
    static void clearEffects()throws Exception {set("a",null,"b","Ljava/util/Vector;",new Vector(24));set("a",null,"c","Z",false);set("a",null,"a","[Ljavax/microedition/lcdui/Image;",new Image[4]);decoder(false);}
    static Object raw(int kind,boolean loops,int frames,int delay,int duration)throws Exception {
        return make("a",new Class<?>[]{int.class,byte.class,boolean.class,int.class,int.class,int.class},kind,(byte)0,loops,frames,delay,duration);
    }
    static void events()throws Exception {
        for(String n:new String[]{"b","k","j","n"})add(n+":"+C(n).getField("events").get(null));
        add("media:"+Manager.calls.toString());add("images:"+Image.calls.toString());
        Object rng=get("k",null,"a","Ljava/util/Random;");if(rng instanceof FixedRandom)add("rng:"+((FixedRandom)rng).count);
    }
    static void resetEvents()throws Exception {
        for(String n:new String[]{"b","k","j","n"})((StringBuilder)C(n).getField("events").get(null)).setLength(0);
        Image.reset(0,0);Manager.calls.clear();
    }
    static void world()throws Exception {
        for(String n:new String[]{"a","i","f","p","d","o"})add("b"+n+":"+get("b",null,n,"B"));
        add("score:"+get("b",null,"a","S"));add("timer:"+get("b",null,"s","I"));
        add("rise:"+get("o",null,"n","I")+":"+get("o",null,"o","I"));
        record(get("b",null,"b","Lj;"));add("ammo:"+value(get("j",null,"a","[B"),0));
        record(get("k",null,"a","Lg;"));events();
    }
    static Graphics graphics()throws Exception{return (Graphics)get("k",null,"a","Ljavax/microedition/lcdui/Graphics;");}
    static void newGraphics(int fail)throws Exception {Graphics g=new Graphics();g.throwAtDraw=fail;set("k",null,"a","Ljavax/microedition/lcdui/Graphics;",g);}
    static void resources()throws Exception {
        decoder(false);Image.reset(0,0);
        ok(invoke("s",null,"a","(Ljava/lang/Class;)V",EntityProbe.class));
        clearEffects();ok(invoke("a",null,"a","(Ljava/lang/Class;)V",EntityProbe.class));
        ok(invoke("a",null,"a","()V"));
        Object font=make("l",new Class<?>[]{String.class,String.class,String.class},"fnt1","/fnt1.font","/fnt1.def");ok(font);
        set("k",null,"a","Ll;",font);
        set("c",null,"a","Ljavax/microedition/lcdui/Image;",Image.createImage("/pics/alienWeapons.png"));
        set("b",null,"b","Ljavax/microedition/lcdui/Image;",Image.createImage("/pics/Hud.png"));
        set("b",null,"o","B",(byte)16);
        resetWorld();
    }
    static void resetWorld()throws Exception {
        for(String n:new String[]{"a","i","f","p","d"})set("b",null,n,"B",(byte)0);
        for(String n:new String[]{"a","b","c"})set("b",null,n,"S",(short)0);
        set("b",null,"s","I",0);C("b").getField("failSelect").setInt(null,0);C("n").getField("failure").setInt(null,0);
        C("b").getField("bucket").set(null,C("n").newInstance());
        set("k",null,"c","I",0);C("k").getField("inputMask").setInt(null,0);
        set("k",null,"a","Ljava/util/Random;",new FixedRandom(7,false));
        set("o",null,"n","I",0);set("o",null,"o","I",0);
        Object player=xyz("j",0,0,0);ok(player);set("b",null,"b","Lj;",player);
        set("j",null,"a","[B",new byte[12]);byte[] max=new byte[12];Arrays.fill(max,(byte)10);set("c",null,"a","[B",max);
        Object sound=make("g",new Class<?>[0]);ok(sound);ok(invoke("g",sound,"a","(I)V",5));
        byte[][] samples=new byte[5][];for(int n=0;n<5;++n)samples[n]=new byte[]{1,2};set("g",sound,"a","[[B",samples);
        set("k",null,"a","Lg;",sound);Manager.reset();resetEvents();newGraphics(-1);
    }
    static byte[] bytes(String path)throws Exception {InputStream in=EntityProbe.class.getResourceAsStream(path);if(in==null)throw new AssertionError(path);ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1)out.write(b,0,n);in.close();return out.toByteArray();}
    static void effectsLoad()throws Exception {
        byte[] data=bytes("/data/effects.dat");ResourceLoader loader=new ResourceLoader(bytes("/EntityResourceOwner.class"));Class<?> owner=loader.owner();
        for(int second=0;second<2;++second)for(int cut=-1;cut<=data.length;++cut) {
            clearEffects();decoder(second==1);loader.data=cut<0?null:Arrays.copyOf(data,cut);loader.fail=-1;
            invoke("a",null,"a","(Ljava/lang/Class;)V",owner);statics("a");add("decoder:"+get("e",null,"a","B")+":"+get("e",null,"a","Z"));
        }
        for(int fault=0;fault<40;++fault) {
            clearEffects();loader.data=data;loader.fail=fault;
            invoke("a",null,"a","(Ljava/lang/Class;)V",owner);statics("a");
        }
        clearEffects();loader.data=data;loader.fail=-1;
        for(int n=0;n<3;++n){invoke("a",null,"a","(Ljava/lang/Class;)V",owner);statics("a");}
        for(int count:new int[]{0,127,128,255}) {
            clearEffects();loader.data=new byte[72];for(int n=0;n<24;++n)loader.data[n*3+2]=(byte)count;
            invoke("a",null,"a","(Ljava/lang/Class;)V",owner);statics("a");
        }
    }
    static void effectsState()throws Exception {
        clearEffects();invoke("a",null,"a","(Ljava/lang/Class;)V",EntityProbe.class);
        for(int index=-2;index<26;++index){Object obj=make("a",new Class<?>[]{int.class},index);record(obj);events();}
        Random rng=new Random(73119L);
        for(int n=0;n<4096;++n) {
            Object obj=raw(n%26,(n&1)==0,EDGE[n%EDGE.length],EDGE[(n/7)%EDGE.length],rng.nextInt());ok(obj);
            set("a",obj,"a","S",(short)EDGE[(n/11)%EDGE.length]);set("a",obj,"a","B",(byte)n);
            set("a",obj,"d","B",(byte)(n>>3));set("a",null,"a","Z",(n&2)!=0);
            record(obj);
            for(int j=0;j<9;++j){invoke("a",obj,"b","()V");record(obj);}
        }
        // Cross product avoids correlating kind 1 with non-looping odd cases.
        for(int kind:new int[]{1,18,0,7})for(boolean loop:new boolean[]{false,true})
        for(boolean alternate:new boolean[]{false,true})for(short last:new short[]{-1,0,3,5,127}) {
            Object obj=raw(kind,loop,6,0,2);ok(obj);
            set("a",obj,"a","S",last);set("a",null,"a","Z",alternate);
            for(int frame=-128;frame<128;++frame){set("a",obj,"a","B",(byte)frame);set("a",obj,"d","B",(byte)0);invoke("a",obj,"b","()V");record(obj);}
        }
        clearEffects(); // Exercise automatic real-resource initialization and shared frame vectors.
        Object first=make("a",new Class<?>[]{int.class},0);ok(first);
        Object second=make("a",new Class<?>[]{int.class},0);ok(second);
        add("shared:"+(get("a",first,"a","Ljava/util/Vector;")==get("a",second,"a","Ljava/util/Vector;")));
        for(int f=0;f<4;++f){set("a",null,"a","[Ljavax/microedition/lcdui/Image;",new Image[4]);Image.reset(1,f);invoke("a",null,"a","()V");statics("a");events();}
    }
    static void effectsDraw()throws Exception {
        resources();Vector templates=(Vector)get("a",null,"b","Ljava/util/Vector;");
        for(int kind=0;kind<24;++kind) {
            Object obj=make("a",new Class<?>[]{int.class},kind);ok(obj);
            int count=((Number)get("a",obj,"b","S")).intValue();
            for(int frame=-1;frame<=count;++frame)for(int pass=0;pass<3;++pass) {
                set("a",obj,"a","B",(byte)frame);newGraphics(pass==2?1:-1);
                int x=pass==0?40:Integer.MAX_VALUE,y=pass==0?50:-17;
                invoke("a",obj,"a","(II)V",x,y);record(obj);add(graphics().snapshot());
            }
        }
        Object obj=raw(7,true,2,0,1);ok(obj);set("a",obj,"a","Ljava/util/Vector;",null);
        newGraphics(-1);invoke("a",obj,"c","()V");record(obj);add(graphics().snapshot());
        set("a",null,"a","[Ljavax/microedition/lcdui/Image;",new Image[4]);
        invoke("a",obj,"c","()V");record(obj);add(graphics().snapshot());
    }
    static void entityCore()throws Exception {
        resources();Random random=new Random(883L);
        for(int type=-260;type<=390;++type) {
            Object obj=xyz("o",EDGE[Math.floorMod(type,EDGE.length)],type,type);record(obj);events();resetEvents();
            invoke("o",null,"a","(I)Z",type);
            for(int threshold:new int[]{-128,6,7,127}) {
                set("b",null,"p","B",(byte)threshold);
                Object value=invoke("o",null,"a","(III)Lo;",type*257,~type,type);record(value);events();resetEvents();
            }
        }
        Object obj=xyz("o",0,0,0);ok(obj);
        for(int n=0;n<14000;++n) {
            set("o",obj,"k","I",EDGE[n%EDGE.length]);set("o",obj,"l","I",EDGE[(n/13)%EDGE.length]);
            set("o",obj,"q","B",(byte)(n%130));set("b",null,"b","S",(short)random.nextInt());set("b",null,"c","S",(short)random.nextInt());
            invoke("o",obj,"a","(II)Z",n%2==0?random.nextInt():EDGE[n%EDGE.length],n%3==0?random.nextInt():EDGE[(n/3)%EDGE.length]);
            record(obj);
        }
        // Deliberate edge contact rather than relying on low-probability random hits.
        set("o",obj,"q","B",(byte)58);
        for(int x:new int[]{Integer.MIN_VALUE,-32768,0,32767,Integer.MAX_VALUE})
        for(int size:new int[]{-128,-1,0,1,7,127}) {
            set("o",obj,"k","I",x);set("o",obj,"l","I",x);
            set("b",null,"b","S",(short)0);set("b",null,"c","S",(short)0);
            ((byte[])get("s",null,"b","[B"))[58]=(byte)size;((byte[])get("s",null,"c","[B"))[58]=(byte)size;
            for(int dx:new int[]{-1,0,size,size+1})for(int dy:new int[]{-1,0,size,size+1})invoke("o",obj,"a","(II)Z",x+dx,x+dy);
        }
        invoke("o",obj,"a","()V");record(obj);
    }
    static void entityUpdate()throws Exception {
        resources();int[] flags={0,1,15,16,65535,65536,-1,Integer.MIN_VALUE};
        long[] longs={Long.MIN_VALUE,-1,0,1,7,Long.MAX_VALUE};
        for(int n=0;n<3600;++n) {
            resetWorld();boolean pickup=n%4==0;Object obj=xyz(pickup?"i":"o",20,30,pickup?12:58);ok(obj);
            Object effect=raw(n%7,true,5,n%5,2);ok(effect);set("a",effect,"a","S",(short)4);
            set("a",effect,"a","J",longs[n%longs.length]);set("a",effect,"b","J",longs[(n/6)%longs.length]);
            set("o",obj,"c","La;",n%3==0?null:effect);set("o",obj,"m","I",flags[n%flags.length]);
            set("o",null,"n","I",EDGE[(n/7)%EDGE.length]);set("o",null,"o","I",EDGE[(n/11)%EDGE.length]);
            set("k",null,"c","I",EDGE[(n/5)%EDGE.length]);C("k").getField("inputMask").setInt(null,n%2==0?16:0);
            set("b",null,"a","B",(byte)(n%3==0?6:0));set("b",null,"a","S",(short)(n%2==0?32767:-32768));
            set("b",null,"i","B",(byte)127);set("b",null,"f","B",(byte)127);
            C("b").getField("failSelect").setInt(null,n%19==0?2:n%23==0?1:0);
            C("n").getField("failure").setInt(null,n%17==0?1:0);
            for(int t=0;t<3;++t){invoke("o",obj,"f","()V");record(obj);world();}
        }
    }
    static void updateIntegration()throws Exception {
        // Explicitly exercise inherited update -> real pickup -> real audio,
        // including the original double removal and the full-stat early return.
        for(int type:new int[]{12,13,14,15,16,26,58})for(int flags:new int[]{65536,-1,16})
        for(int health:new int[]{0,100})for(int mode:new int[]{0,6}) {
            resetWorld();Object obj=xyz(type==58?"o":"i",20,30,type);ok(obj);
            set("o",obj,"m","I",flags);set("o",null,"n","I",8);set("o",null,"o","I",4);
            set("b",null,"a","B",(byte)mode);set("j",get("b",null,"b","Lj;"),"e","S",(short)health);
            invoke("o",obj,"f","()V");record(obj);world();
        }
        // Interleaving entities must not silently make the original shared rise counter per-instance.
        resetWorld();Object first=xyz("o",0,100,58),second=xyz("o",0,100,58);ok(first);ok(second);
        set("o",first,"m","I",65536);set("o",second,"m","I",65536);
        set("o",null,"n","I",1);set("o",null,"o","I",16);
        for(int tick=0;tick<4;++tick){invoke("o",first,"f","()V");invoke("o",second,"f","()V");record(first);record(second);world();}
    }
    static void pickupState()throws Exception {
        resources();int[] health={-32768,-1,0,49,50,99,100,101,32760,32767};
        for(int type=12;type<=35;++type)for(int h:health)for(int variation=0;variation<8;++variation) {
            resetWorld();Object obj=xyz("i",20,30,type);ok(obj);
            Object player=get("b",null,"b","Lj;");set("j",player,"e","S",(short)h);
            set("b",null,"d","B",(byte)(variation&1));
            if(variation==2)set("b",null,"b","Lj;",null);
            if(variation==3)set("j",null,"a","[B",get("c",null,"a","[B"));
            if(variation==4)set("c",null,"a","[B",new byte[0]);
            if(variation==5)C("b").getField("failSelect").setInt(null,1);
            if(variation==6)set("k",null,"a","Lg;",null);
            if(variation==7){Object sound=get("k",null,"a","Lg;");set("g",sound,"a","I",0);Manager.faultPoint=1;Manager.faultMode=2;Manager.remaining=1;}
            invoke("i",obj,"i","()V");record(obj);world();
            invoke("i",obj,"i","()V");record(obj);world();
        }
        for(int fail=0;fail<4;++fail){Image.reset(1,fail);invoke("i",null,"b","()V");statics("i");invoke("i",null,"c","()V");statics("i");events();}
    }
    static void entityDraw()throws Exception {
        resources();
        for(int type=12;type<=35;++type)for(int tick=0;tick<8;++tick) {
            Object obj=xyz("i",40,60,type);ok(obj);set("k",null,"c","I",tick);newGraphics(tick==7?0:-1);
            invoke("i",obj,"g","()V");record(obj);add(graphics().snapshot());
        }
        Object pickup=xyz("i",Integer.MIN_VALUE,Integer.MAX_VALUE,12);ok(pickup);
        for(String method:new String[]{"d","e","h"}){newGraphics(-1);invoke("i",pickup,method,"()V");add(graphics().snapshot());}
        for(int v:EDGE)for(String method:new String[]{"a","b"}){newGraphics(-1);invoke("i",pickup,method,"(I)V",v);add(graphics().snapshot());}
        Object column=xyz("h",40,150,3);ok(column);
        set("h",column,"a","Ljavax/microedition/lcdui/Image;",Image.createImage("/pics/Beam.png"));
        ((byte[])get("s",null,"b","[B"))[3]=32;((byte[])get("s",null,"c","[B"))[3]=110;
        for(int phase=-128;phase<128;++phase)for(int tick=0;tick<2;++tick){
            set("h",column,"a","B",(byte)phase);set("k",null,"c","I",tick);newGraphics(phase==2?1:-1);
            invoke("h",column,"g","()V");invoke("h",column,"b","()V");record(column);add(graphics().snapshot());
        }
        for(int height:new int[]{-128,-1,0,17,18,19,127})for(int phase=0;phase<7;++phase) {
            ((byte[])get("s",null,"c","[B"))[3]=(byte)height;
            set("h",column,"a","B",(byte)phase);set("k",null,"c","I",1);
            set("b",null,"b","S",(short)-32768);set("b",null,"c","S",(short)32767);
            newGraphics(-1);invoke("h",column,"g","()V");invoke("h",column,"b","()V");record(column);add(graphics().snapshot());
        }
        Object base=xyz("o",40,60,58);ok(base);Object effect=make("a",new Class<?>[]{int.class},7);ok(effect);
        for(int flags:new int[]{0,1,16,65536,-1}){
            set("o",base,"m","I",flags);set("o",base,"c","La;",effect);newGraphics(-1);
            invoke("o",base,"g","()V");record(base);add(graphics().snapshot());
        }
        set("o",base,"q","B",(byte)127);newGraphics(-1);invoke("o",base,"g","()V");add(graphics().snapshot());
    }
    static void attachmentState()throws Exception {
        resources();
        for(int type=0;type<127;++type) {
            set("k",null,"a","Ljava/util/Random;",new FixedRandom(type,false));
            Object obj=xyz("m",type,40,type);record(obj);events();resetEvents();
        }
        Object obj=xyz("m",Integer.MAX_VALUE,Integer.MIN_VALUE,0);ok(obj);
        for(int n=0;n<512;++n) {
            byte type=(byte)(n%128);set("o",obj,"q","B",type);set("m",obj,"b","B",(byte)99);
            set("k",null,"a","Ljava/util/Random;",n%5==0?null:new FixedRandom(n,n%7==0));
            invoke("m",obj,"b","()V");record(obj);record(get("m",obj,"a","Lo;"));events();resetEvents();
        }
        set("o",obj,"q","B",(byte)65);set("o",obj,"m","I",0);
        for(int kind=0;kind<5;++kind) {
            Object child=kind==0?null:xyz(kind==1?"o":"j",40,50,kind==4?6:5);ok(child);
            if(kind>=2)set("j",child,"c","Z",kind==3);
            set("m",obj,"a","Lo;",child);newGraphics(-1);invoke("m",obj,"f","()V");record(obj);
            invoke("m",obj,"g","()V");record(obj);add(graphics().snapshot());events();resetEvents();
        }
    }
    public static void main(String[] args)throws Exception {
        candidate=Boolean.parseBoolean(args[0]);digest=MessageDigest.getInstance("SHA-256");
        BufferedReader in=new BufferedReader(new InputStreamReader(EntityProbe.class.getResourceAsStream("/aliases.tsv"),"UTF-8"));String line;
        while((line=in.readLine())!=null){String[] p=line.split("\t");if(p.length!=5)throw new AssertionError("Alias format");aliases.put(p[0]+"\t"+p[1]+"\t"+p[2]+"\t"+p[3],p[4]);}in.close();
        String mode=args[1];
        if(mode.equals("effects-load"))effectsLoad();else if(mode.equals("effects-state"))effectsState();
        else if(mode.equals("effects-draw"))effectsDraw();else if(mode.equals("entity-core"))entityCore();
        else if(mode.equals("entity-update")){entityUpdate();updateIntegration();}else if(mode.equals("pickup-state"))pickupState();
        else if(mode.equals("entity-draw"))entityDraw();else if(mode.equals("attachment-state"))attachmentState();else throw new AssertionError(mode);
        if(successes==0)throw new AssertionError("No successful target calls");
        add("successes:"+successes+";exceptions:"+failures);
        StringBuilder hex=new StringBuilder();for(byte b:digest.digest())hex.append(String.format("%02x",b&255));
        System.out.println(mode+"\t"+calls+"\t"+hex);System.err.println("successful="+successes+" expected-or-recorded-exceptions="+failures+" fixture_calls="+fixtureCalls);
        for(Map.Entry<String,long[]> row:outcomes.entrySet())System.err.println("METHOD\t"+row.getKey()+"\t"+row.getValue()[0]+"\t"+row.getValue()[1]);
    }
    public static final class FixedRandom extends Random {
        final int fixed;final boolean fail;int count;
        FixedRandom(int fixed,boolean fail){super(0);this.fixed=fixed;this.fail=fail;}
        public int nextInt(){++count;if(fail)throw new IllegalStateException("scripted RNG");return fixed;}
    }
    static final class ResourceLoader extends ClassLoader {
        byte[] data,ownerBytes;int fail=-1;
        ResourceLoader(byte[] code){super(null);ownerBytes=code;}
        Class<?> owner(){return defineClass("EntityResourceOwner",ownerBytes,0,ownerBytes.length);}
        public InputStream getResourceAsStream(String name) {
            if(!name.equals("data/effects.dat")||data==null)return null;
            final byte[] copy=data;final int fault=fail;
            return new InputStream(){int pos;public int read()throws IOException{
                if(pos==fault)throw new IOException("scripted read");return pos<copy.length?copy[pos++]&255:-1;}};
        }
    }
}
/** Independently authored resource identity for controlled Class.getResourceAsStream tests. */
final class EntityResourceOwner { }
