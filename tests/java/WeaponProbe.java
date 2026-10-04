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
public final class WeaponProbe {
    static boolean candidate;
    static final Map<String,String> aliases = new HashMap<String,String>();
    static final Map<String,Field> fields = new HashMap<String,Field>();
    static final Map<String,Method> methods = new HashMap<String,Method>();
    static MessageDigest digest;
    static long calls, successes, failures, fixtureCalls;
    static final Set<String> TARGETS = new HashSet<String>(Arrays.asList("c","f","GameMidlet"));
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
        try {Constructor<?> ct=C(c).getDeclaredConstructor(types);ct.setAccessible(true);Object v=ct.newInstance(args);++successes;track(c,"<init>",cd.toString(),true);add("new:"+c);oid(v);return v;}
        catch(InvocationTargetException e){Throwable t=e.getCause();
            if(t instanceof LinkageError)throw new AssertionError("Broken constructor linkage",t);
            ++failures;track(c,"<init>",cd.toString(),false);add("constructor-throw:"+c+":"+t.getClass().getName());return t;
        }
    }
    static Object xyz(String c,int x,int y,int id)throws Exception{return make(c,new Class<?>[]{int.class,int.class,int.class},x,y,id);}
    static void ok(Object v) {if(v instanceof Throwable)throw new AssertionError("Unexpected fixture failure",(Throwable)v);}
    static void add(String s)throws Exception {if(Boolean.getBoolean("dah.trace"))System.err.println("TRACE:"+s);byte[] b=s.getBytes("UTF-8");digest.update((byte)(b.length>>>24));digest.update((byte)(b.length>>>16));digest.update((byte)(b.length>>>8));digest.update((byte)b.length);digest.update(b);}
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
        if(C("o").isInstance(v))return entitySig(v);
        return "ref:"+v.getClass().getName()+":"+oid(v);
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

    static IdentityHashMap<Object,Integer> ids=new IdentityHashMap<Object,Integer>();
    static int oid(Object v){if(v==null)return 0;Integer id=ids.get(v);if(id==null){id=ids.size()+1;ids.put(v,id);}return id;}
    static String entitySig(Object v)throws Exception {
        if(v==null)return "null";
        String out=v.getClass().getName()+"#"+oid(v)+":";
        for(String[] f:new String[][]{{"k","I"},{"l","I"},{"o","B"},{"p","B"},{"q","B"},{"m","I"},{"g","Z"}})out+=get("o",v,f[0],f[1])+",";
        if(C("j").isInstance(v))for(String[] f:new String[][]{{"g","B"},{"c","S"},{"b","S"},{"a","S"},{"e","S"},{"f","B"}})out+="j"+f[0]+":"+get("j",v,f[0],f[1])+",";
        if(C("r").isInstance(v))out+="part:"+get("r",v,"a","B")+",width:"+get("r",v,"a","I")+",height:"+get("r",v,"b","I")+",owner:"+oid(get("r",v,"a","Ld;"));
        if(C("m").isInstance(v))out+=",child:"+oid(get("m",v,"a","Lo;"));
        return out;
    }
    static final class FixedRandom extends Random {
        final int[] values; int count; int failAt=-1;
        FixedRandom(int... v) { values=v; }
        public int nextInt() {if(count==failAt)throw new IllegalStateException("scripted random");return values[(count++)%values.length];}
    }
    static void decoder()throws Exception {set("e",null,"a","B",(byte)0);set("e",null,"a","Z",false);}
    static void resources()throws Exception {
        decoder();Image.reset(0,0);ok(invoke("s",null,"a","(Ljava/lang/Class;)V",WeaponProbe.class));
        set("a",null,"c","Z",false);set("a",null,"b","Ljava/util/Vector;",new Vector(24));decoder();
        ok(invoke("a",null,"a","(Ljava/lang/Class;)V",WeaponProbe.class));ok(invoke("a",null,"a","()V"));
        // Record the actual static weapon arrays/image before any instance tests.
        statics("c");
        reset();
    }
    static void reset()throws Exception {
        ids.clear();
        for(String n:new String[]{"a","i","f","p","d"})set("b",null,n,"B",(byte)0);
        for(String n:new String[]{"a","b","c"})set("b",null,n,"S",(short)0);
        set("b",null,"d","S",(short)800);set("b",null,"h","S",(short)3);set("b",null,"i","S",(short)4);
        set("b",null,"g","S",(short)256);set("b",null,"f","S",(short)256);
        set("b",null,"k","B",(byte)1);set("b",null,"j","I",0);set("b",null,"f","Z",false);
        set("b",null,"o","B",(byte)16);set("b",null,"s","I",0);set("b",null,"e","I",12345);
        set("b",null,"b","B",(byte)0);set("b",null,"a","[Lo;",Array.newInstance(C("o"),256));
        for(String owner:new String[]{"b","j","k"})for(Field f:C(owner).getFields())if(f.getName().startsWith("fail")&&f.getType()==int.class)f.setInt(null,0);
        C("j").getField("changeHealth").setBoolean(null,false);
        C("b").getField("interception").set(null,null);
        set("k",null,"a","I",176);set("k",null,"b","I",208);set("k",null,"c","I",50);C("k").getField("inputMask").setInt(null,0);
        set("k",null,"a","Ljava/util/Random;",new FixedRandom(7,-1,Integer.MIN_VALUE,16));
        set("o",null,"n","I",0);set("o",null,"o","I",8);
        set("j",null,"a","[B",new byte[16]);Arrays.fill((byte[])get("j",null,"a","[B"),(byte)-1);
        set("j",null,"d","Z",false);set("j",null,"d","I",0);set("j",null,"j","I",0);
        set("f",null,"a","I",100);set("f",null,"b","Z",false);
        Object group=make("n",new Class<?>[]{int.class,int.class},0,0);ok(group);C("b").getField("bucket").set(null,group);
        Object cells=Array.newInstance(C("n"),12);for(int index=0;index<12;index++)Array.set(cells,index,group);set("b",null,"a","[Ln;",cells);
        Object player=xyz("j",30,40,0);ok(player);set("b",null,"b","Lj;",player);set("b",null,"a","Lj;",player);set("b",null,"a","Lf;",null);
        Object sound=make("g",new Class<?>[0]);ok(sound);ok(invoke("g",sound,"a","(I)V",5));
        byte[][] samples=new byte[5][];for(int index=0;index<5;index++)samples[index]=new byte[]{1,2};set("g",sound,"a","[[B",samples);set("k",null,"a","Lg;",sound);
        clearEvents();newGraphics(-1);
    }
    static void clearEvents()throws Exception {
        for(String n:new String[]{"b","k","j"})((StringBuilder)C(n).getField("events").get(null)).setLength(0);
        Image.reset(0,0);Manager.reset();
    }
    static void events()throws Exception {
        for(String n:new String[]{"b","k","j"})add(n+":"+C(n).getField("events").get(null));
        add("images:"+Image.calls);add("media:"+Manager.calls);
        Object random=get("k",null,"a","Ljava/util/Random;");if(random instanceof FixedRandom)add("rng:"+((FixedRandom)random).count);
    }
    static Graphics graphics()throws Exception {return (Graphics)get("k",null,"a","Ljavax/microedition/lcdui/Graphics;");}
    static void newGraphics(int fail)throws Exception {Graphics g=new Graphics();g.throwAtDraw=fail;set("k",null,"a","Ljavax/microedition/lcdui/Graphics;",g);}
    static Object weapon(Object owner)throws Exception {Object w=make("c",new Class<?>[]{C("j")},owner);ok(w);set("j",owner,"a","Lc;",w);return w;}
    static Object actor(int type)throws Exception {
        Object result=xyz(type==6?"f":"j",30,40,type);ok(result);
        // Put the saucer in the exercised viewport after its original constructor.
        set("o",result,"k","I",30);set("o",result,"l","I",40);
        if(type==6)set("b",null,"a","Lf;",result);
        if(type==0) {set("b",null,"a","Lj;",result);set("b",null,"b","Lj;",result);}
        return result;
    }
    static void observe(Object w)throws Exception {
        record(w);
        if(w!=null&&!(w instanceof Throwable)) {
            Object owner=get("c",w,"a","Lj;"),target=get("c",w,"a","Lo;");
            if(owner!=null)record(owner);if(target!=null)record(target);
            add("effectAliases:"+oid(get("c",w,"a","La;"))+","+oid(get("c",w,"b","La;"))+","+oid(get("c",w,"c","La;")));
        }
        add("ammo:"+value(get("j",null,"a","[B"),0));add("fshield:"+get("f",null,"a","I")+":"+get("f",null,"b","Z"));
        add("rise:"+get("o",null,"n","I")+":"+get("o",null,"o","I"));add("cycle:"+get("a",null,"a","Z"));
        events();
    }
    static Object obj(int type)throws Exception {Object o=xyz(type>=12&&type<=35?"i":"o",70,70,type);ok(o);return o;}
    static void selection()throws Exception {
        resources();
        for(int type:new int[]{0,1,2,3,4,5,6,7,37})for(int direction:new int[]{-1,0,1,2,3,4}) {
            reset();Object owner=actor(type);set("j",owner,"f","B",(byte)direction);Object w=weapon(owner);
            observe(w);
            for(int value:new int[]{-129,-128,-1,0,1,2,3,4,5,6,7,8,9,10,14,15,127,128,255}) {
                invoke("c",w,"a","(I)V",value);observe(w);
                invoke("c",w,"a","(B)V",(byte)value);observe(w);
            }
        }
        reset();make("c",new Class<?>[]{C("j")},new Object[]{null});events();
        Object owner=actor(0),w=weapon(owner);
        // Coordinate/table failures occur before the mode switch; preserve partial writes.
        for(int type:new int[]{-128,-1,127}) {set("o",owner,"q","B",(byte)type);invoke("c",w,"a","(B)V",(byte)0);observe(w);}
    }
    static Object section()throws Exception {
        decoder();ok(invoke("d",null,"a","(Ljava/lang/Object;)Z",new WeaponProbe()));
        Object v=make("r",new Class<?>[]{C("d"),C("d"),byte.class,int.class,int.class,byte.class,byte.class},null,null,(byte)0,70,70,(byte)31,(byte)27);ok(v);return v;
    }
    static Object target(int kind)throws Exception {
        if(kind==0)return null;if(kind==1)return xyz("j",70,70,1);if(kind==2)return xyz("j",70,70,3);
        if(kind==3)return obj(58);if(kind==4)return obj(12);if(kind==5)return section();
        if(kind==6)return xyz("m",70,70,65);return obj(40);
    }
    static void aiming()throws Exception {
        resources();
        for(int type:new int[]{0,2,6})for(int dir=-1;dir<5;dir++) {
            reset();Object owner=actor(type),w=weapon(owner);set("j",owner,"f","B",(byte)dir);
            for(int kind=0;kind<8;kind++) {
                Object t=target(kind);for(int id:new int[]{0,1,4,7}) {
                    set("c",w,"h","I",id);invoke("c",w,"a","(Lo;)Z",t);observe(w);
                    invoke("c",w,"a","()V");observe(w);
                }
            }
        }
        reset();Object w=weapon(actor(0));
        for(int x:EDGE)for(int y:EDGE) {
            set("c",w,"d","I",y);set("c",w,"e","I",x);
            for(int speed:new int[]{0,1,10,-1,Integer.MIN_VALUE}) {
                set("c",w,"l","I",speed);invoke("c",w,"a","(II)V",x,y);record(w);
            }
        }
        // Intentional cast/null failure in the type-6 fallback path.
        reset();Object impostor=xyz("j",30,40,6),wi=weapon(impostor);invoke("c",wi,"a","()V");observe(wi);
        reset();Object ship=actor(6);w=get("j",ship,"a","Lc;");set("f",ship,"a","Lj;",null);invoke("c",w,"a","()V");observe(w);
    }
    static void firing()throws Exception {
        resources();
        for(int ownerType:new int[]{0,2,3,5,6}) {
            reset();Object owner=actor(ownerType),w=weapon(owner);
            Object[] targets=new Object[]{null,xyz("j",70,70,0),xyz("j",70,70,1),xyz("j",70,70,3),xyz("j",70,70,4),xyz("j",70,70,5),obj(58),obj(12),obj(40)};
            for(Object victim:targets)for(int id:new int[]{0,1,2,4,6,7,9,14})for(int state:new int[]{0,8,11,13,15,16,17,18}) {
                clearEvents();set("j",owner,"g","B",(byte)0);set("j",owner,"f","B",(byte)1);
                set("o",owner,"q","B",(byte)ownerType);set("o",owner,"k","I",30);set("o",owner,"l","I",40);
                if(victim!=null){set("o",victim,"m","I",0);if(C("j").isInstance(victim)){set("j",victim,"g","B",(byte)state);weapon(victim);}}
                invoke("c",w,"a","(I)V",id);set("c",w,"a","Lo;",victim);invoke("c",w,"a","()V");
                set("b",null,"a","B",(byte)0);C("b").getField("interception").set(null,null);
                invoke("c",w,"b","()V");observe(w);
            }
            // Owner-state gate is independent of target-state gate.
            Object victim=xyz("j",70,70,1);weapon(victim);
            for(int id:new int[]{0,1,2,4,7})for(int state=-1;state<20;state++) {
                invoke("c",w,"a","(I)V",id);set("c",w,"a","Lo;",victim);set("j",victim,"g","B",(byte)0);
                set("j",owner,"g","B",(byte)state);invoke("c",w,"b","()V");observe(w);
            }
        }
        for(int fault=0;fault<11;fault++) {
            reset();Object owner=actor(0),w=weapon(owner),victim=xyz("j",70,70,1);weapon(victim);
            invoke("c",w,"a","(I)V",7);set("c",w,"a","Lo;",victim);invoke("c",w,"a","()V");
            if(fault==1)C("b").getField("failRay").setInt(null,1);
            if(fault==2)C("b").getField("interception").set(null,obj(65));
            if(fault==3) {set("o",victim,"m","I",1);}
            if(fault==4)set("o",owner,"k","I",3000);
            if(fault==5)set("j",null,"a","[B",null);
            if(fault==6) {((byte[])get("j",null,"a","[B"))[7]=0;C("j").getField("failSwitch").setInt(null,1);}
            if(fault==7)set("k",null,"a","Lg;",null);
            if(fault==8) {set("j",null,"d","Z",true);set("j",null,"d","I",127);}
            if(fault==9)C("j").getField("failCall").setInt(null,2);
            if(fault==10)set("c",w,"a","La;",null);
            invoke("c",w,"b","()V");observe(w);
        }
        // Ammo is signed byte state. Positive depletion and the zero fallback are
        // separate from unlimited negative values, range errors and pickup exemptions.
        for(int ownerType:new int[]{0,6})for(int id:new int[]{0,1,3,4,6,7,9})for(int ammo:new int[]{-128,-1,0,1,2,127}) {
            reset();Object owner=actor(ownerType),w=weapon(owner),victim=xyz("j",70,70,1);weapon(victim);
            invoke("c",w,"a","(I)V",id);set("c",w,"a","Lo;",victim);invoke("c",w,"a","()V");
            ((byte[])get("j",null,"a","[B"))[id]=(byte)ammo;
            for(int repeat=0;repeat<3;repeat++) {
                set("j",owner,"g","B",(byte)0);set("j",victim,"g","B",(byte)0);
                invoke("c",w,"b","()V");observe(w);
            }
        }
        // A valid disguise path must complete, rather than only testing bad table indices.
        reset();Object disguised=actor(0),dw=weapon(disguised),victim=xyz("j",70,70,1);weapon(victim);
        set("j",null,"d","Z",true);set("j",null,"d","I",1);set("c",dw,"a","Lo;",victim);
        invoke("c",dw,"a","()V");invoke("c",dw,"b","()V");observe(dw);add("disguise:"+get("j",null,"d","Z"));
        // Exercise a real saucer target, shield/availability, and its own state override.
        reset();Object owner=actor(0),w=weapon(owner),ship=actor(6);
        for(int state:new int[]{0,8,15,18})for(int id:new int[]{0,2,4,7})for(int shield:new int[]{-1,0,1,100}) {
            clearEvents();set("j",owner,"g","B",(byte)0);set("j",ship,"g","B",(byte)state);set("f",null,"a","I",shield);
            invoke("c",w,"a","(I)V",id);set("c",w,"a","Lo;",ship);invoke("c",w,"b","()V");observe(w);
        }
        set("f",null,"b","Z",true);set("j",owner,"g","B",(byte)0);invoke("c",w,"b","()V");observe(w);
    }
    static void projectileUpdate()throws Exception {
        resources();
        for(int ownerType:new int[]{0,2,6}) {
            reset();Object owner=actor(ownerType),w=weapon(owner);Object[] targets={null,xyz("j",70,70,1),obj(58),obj(12),obj(40),section()};
            for(Object target:targets)for(int id:new int[]{0,2,3,4,5,6,7,9,14})for(boolean hit:new boolean[]{false,true}) {
                for(int tick=0;tick<12;tick++) {
                    if(tick==0) {invoke("c",w,"a","(I)V",id);set("c",w,"a","Lo;",target);invoke("c",w,"a","()V");set("c",w,"f","I",30<<16);set("c",w,"g","I",40<<16);set("c",w,"b","Z",hit);}
                    set("j",owner,"f","B",(byte)(tick%4));invoke("c",w,"c","()V");observe(w);
                }
            }
        }
        reset();Object w=weapon(actor(0)),v=obj(40);set("c",w,"a","Lo;",v);
        for(int value:EDGE) {
            set("c",w,"b","Z",false);set("c",w,"f","I",value);set("c",w,"g","I",~value);set("c",w,"i","I",Integer.MAX_VALUE);set("c",w,"j","I",Integer.MIN_VALUE);
            invoke("c",w,"c","()V");observe(w);
        }
        set("c",w,"a","Z",true);set("c",w,"a","I",77);set("c",w,"a","B",(byte)0);set("c",w,"b","Z",false);set("c",w,"f","I",80<<16);set("c",w,"g","I",80<<16);C("b").getField("failBlast").setInt(null,1);
        invoke("c",w,"c","()V");observe(w);
    }
    static void drawing()throws Exception {
        resources();
        for(int type:new int[]{0,3,6}) {
            reset();Object owner=actor(type),w=weapon(owner);
            for(int id:new int[]{0,1,2,3,4,5,6,7,9,14})for(int direction:new int[]{0,1,2,3})for(int fault:new int[]{-1,0,1,3}) {
                invoke("c",w,"a","(I)V",id);set("j",owner,"f","B",(byte)direction);
                set("c",w,"f","I",90<<16);set("c",w,"g","I",110<<16);set("c",w,"b","I",40);set("c",w,"c","I",40);
                newGraphics(fault);clearEvents();invoke("c",w,"d","()V");record(w);add(graphics().snapshot());events();
            }
            for(int kind=-1;kind<20;kind++) {
                newGraphics(-1);invoke("c",w,"b","(I)V",kind);record(w);add(graphics().snapshot());events();
            }
        }
        reset();Object w=weapon(actor(0));invoke("c",w,"a","(I)V",3);
        for(int speed:new int[]{-1,0,1,2,10,100,1000,Integer.MIN_VALUE,Integer.MAX_VALUE}) {
            set("c",w,"l","I",speed);set("c",w,"f","I",170<<16);set("c",w,"g","I",200<<16);
            newGraphics(-1);invoke("c",w,"b","(I)V",6);record(w);add(graphics().snapshot());events();
        }
        for(int x:new int[]{-1,0,176,177})for(int y:new int[]{-1,0,208,209}) {
            set("c",w,"f","I",x<<16);set("c",w,"g","I",y<<16);newGraphics(-1);invoke("c",w,"b","(I)V",0);add(graphics().snapshot());
        }
        reset();Object ship=actor(6);w=get("j",ship,"a","Lc;");set("c",w,"a","Lo;",obj(12));newGraphics(-1);invoke("c",w,"b","(I)V",9);add(graphics().snapshot());observe(w);
    }
    static void saucerMotion()throws Exception {
        resources();
        for(int random:EDGE) {
            reset();set("k",null,"a","Ljava/util/Random;",new FixedRandom(random));
            Object ship=xyz("f",123,456,6);record(ship);events();
            if(ship instanceof Throwable)continue;
            invoke("f",ship,"r","()V");record(ship);invoke("f",ship,"a","()V");record(ship);
            for(int dir:new int[]{-128,-1,0,1,2,3,127}) {
                set("j",ship,"f","B",(byte)dir);invoke("f",ship,"b","()V");record(ship);events();
            }
        }
        reset();Object ship=actor(6);
        for(int dir:new int[]{-1,0,1,2,3})for(int step:new int[]{-128,-1,0,1,127})for(int cam:new int[]{-1,0,1,32767}) {
            set("j",ship,"f","B",(byte)dir);set("f",ship,"a","B",(byte)step);set("b",null,"c","S",(short)cam);
            set("o",ship,"k","I",Integer.MAX_VALUE);set("o",ship,"l","I",100);
            invoke("f",ship,"c","()V");record(ship);observe(get("j",ship,"a","Lc;"));
        }
        for(int sourceType:new int[]{0,2,3,4,5,6})for(int shield:new int[]{Integer.MIN_VALUE,-1,0,1,100,Integer.MAX_VALUE})for(int damage:EDGE) {
            set("o",ship,"b","Lj;",xyz("j",0,0,sourceType));set("f",null,"a","I",shield);set("j",ship,"e","S",(short)32767);
            invoke("f",ship,"b","(I)V",damage);record(ship);add("shield:"+get("f",null,"a","I"));
        }
        set("o",ship,"b","Lj;",null);invoke("f",ship,"b","(I)V",9);record(ship);
        set("j",ship,"a","Lc;",null);invoke("f",ship,"c","()V");record(ship);
    }
    static void reticle()throws Exception {
        resources();reset();Object ship=actor(6),cursor=get("f",ship,"a","Lj;");
        for(int state:new int[]{-1,0,8,15})for(int dir:new int[]{-1,0,1,2,3,4})for(int step:new int[]{-128,-1,0,1,8,127})for(int pos:new int[]{-1,0,1,150,300,Integer.MIN_VALUE,Integer.MAX_VALUE}) {
            set("j",ship,"g","B",(byte)state);set("f",ship,"b","B",(byte)dir);set("f",ship,"c","B",(byte)step);
            set("o",cursor,"k","I",pos);set("o",cursor,"l","I",pos);set("b",null,"c","S",(short)30);
            invoke("f",ship,"d","()V");record(ship);record(cursor);
        }
        set("f",ship,"a","Lj;",null);set("j",ship,"g","B",(byte)0);set("f",ship,"b","B",(byte)2);invoke("f",ship,"d","()V");record(ship);
    }
    static void targeting()throws Exception {
        resources();
        for(int kind=0;kind<8;kind++) {
            reset();Object ship=actor(6),cursor=get("f",ship,"a","Lj;"),w=get("j",ship,"a","Lc;");
            set("o",cursor,"k","I",70);set("o",cursor,"l","I",70);
            Object selected=target(kind),group=C("b").getField("bucket").get(null);
            Vector entities=(Vector)get("n",group,"a","Ljava/util/Vector;");if(selected!=null)entities.add(selected);
            if(kind==6)set("m",selected,"a","Lo;",xyz("j",70,70,1));
            for(int x:new int[]{-1,0,70,255,256,768,Integer.MAX_VALUE})for(int y:new int[]{-1,0,70,255,256,1024}) {
                set("o",cursor,"k","I",x);set("o",cursor,"l","I",y);invoke("f",ship,"e","()V");observe(w);
            }
        }
        // Distinct cells expose the original asymmetric -1..0 horizontal scan,
        // clamping and first-match order. Entity coordinates intentionally overlap
        // the cursor; cell placement is controlled independently by this fixture.
        for(int occupied=0;occupied<12;occupied++)for(int start:new int[]{0,1,2}) {
            reset();Object ship=actor(6),cursor=get("f",ship,"a","Lj;"),w=get("j",ship,"a","Lc;");
            set("o",cursor,"k","I",start*256+70);set("o",cursor,"l","I",326);
            Object cells=Array.newInstance(C("n"),12);
            for(int index=0;index<12;index++) {
                Object cell=make("n",new Class<?>[]{int.class,int.class},index%3,index/3);ok(cell);Array.set(cells,index,cell);
                if(index==occupied) {
                    Object v=xyz("j",start*256+70,326,1);ok(v);
                    ((Vector)get("n",cell,"a","Ljava/util/Vector;")).add(v);
                }
            }
            set("b",null,"a","[Ln;",cells);invoke("f",ship,"e","()V");observe(w);
            // Duplicate this same overlapping actor into an earlier/later cell to
            // exercise stable selection with several nonempty neighbors.
            for(int index=0;index<12;index++) {
                Object v=xyz("j",start*256+70,326,1);ok(v);set("j",v,"e","S",(short)index);
                ((Vector)get("n",Array.get(cells,index),"a","Ljava/util/Vector;")).add(v);
            }
            invoke("f",ship,"e","()V");observe(w);
        }
        for(int fault=0;fault<4;fault++) {
            reset();Object ship=actor(6);
            if(fault==0)set("b",null,"g","S",(short)0);
            if(fault==1)set("b",null,"a","[Ln;",null);
            if(fault==2)set("f",ship,"a","Lj;",null);
            if(fault==3)set("b",null,"h","S",(short)0);
            invoke("f",ship,"e","()V");record(ship);events();
        }
    }
    static void saucerUpdateDraw()throws Exception {
        resources();reset();Object ship=actor(6),owner=xyz("j",70,70,1);weapon(owner);set("o",ship,"b","Lj;",owner);
        Object target=xyz("j",70,70,1),w=get("j",ship,"a","Lc;");
        for(int state:new int[]{0,8,15})for(int victimState:new int[]{0,8,12,13,14,17,18})for(int clock:new int[]{-1,0,50,51,100,Integer.MAX_VALUE}) {
            clearEvents();set("j",ship,"g","B",(byte)state);set("j",ship,"e","S",(short)100);set("j",target,"g","B",(byte)victimState);
            set("j",ship,"f","B",(byte)1);set("o",ship,"k","I",50);set("o",ship,"l","I",100);set("f",ship,"b","I",60);
            set("c",w,"a","Lo;",target);set("f",null,"b","Z",true);set("f",null,"a","I",1);set("j",null,"j","I",2);
            Object effect=make("a",new Class<?>[]{int.class},21);ok(effect);set("a",effect,"a","J",0L);set("a",effect,"b","J",50L);set("j",ship,"b","La;",effect);
            set("k",null,"c","I",clock);invoke("f",ship,"f","()V");record(ship);observe(w);add("timer:"+get("j",null,"j","I"));
        }
        for(int frame:new int[]{-1,0,1,2,3,4,127})for(int kind:new int[]{0,5,21})for(boolean visible:new boolean[]{false,true})for(int fault:new int[]{-1,0,1,3}) {
            Object effect=make("a",new Class<?>[]{int.class},kind);ok(effect);set("a",effect,"a","B",(byte)frame);set("a",effect,"a","J",0L);set("a",effect,"b","J",50L);
            set("j",ship,"b","La;",effect);set("j",ship,"g","B",(byte)0);set("k",null,"c","I",50);set("f",ship,"a","Z",visible);set("f",null,"b","Z",true);
            newGraphics(fault);invoke("f",ship,"g","()V");record(ship);add(graphics().snapshot());events();
        }
        // Real weapon/effect drawing through the saucer entry point.
        set("f",ship,"a","Z",true);set("j",ship,"g","B",(byte)8);set("j",ship,"a","La;",get("c",w,"a","La;"));set("j",ship,"b","La;",null);
        newGraphics(-1);invoke("f",ship,"g","()V");record(ship);add(graphics().snapshot());events();
        for(int value:EDGE) {invoke("f",ship,"a","(I)V",value);record(ship);}
        C("j").getField("failTick").setInt(null,1);invoke("f",ship,"f","()V");record(ship);events();
    }
    static void lifecycle()throws Exception {
        resources();statics("GameMidlet"); // Observe its real initial class state before overrides.
        for(int initial:new int[]{-1,0,1,Integer.MAX_VALUE})for(int fault=0;fault<9;fault++) {
            reset();javax.microedition.midlet.MIDlet.events.setLength(0);javax.microedition.midlet.MIDlet.failNew=0;javax.microedition.midlet.MIDlet.failNotify=0;
            javax.microedition.lcdui.Display.events.setLength(0);javax.microedition.lcdui.Display.instance=new javax.microedition.lcdui.Display();
            javax.microedition.lcdui.Display.failGet=0;javax.microedition.lcdui.Display.failSet=0;javax.microedition.lcdui.Display.nullGet=false;
            set("GameMidlet",null,"a","I",initial);set("GameMidlet",null,"b","I",initial);set("GameMidlet",null,"a","Lk;",null);set("GameMidlet",null,"a","Ljavax/microedition/lcdui/Display;",null);
            if(fault==1)javax.microedition.midlet.MIDlet.failNew=1;
            if(fault==2)javax.microedition.lcdui.Display.failGet=1;
            if(fault==3)C("k").getField("failCtor").setInt(null,1);
            if(fault==4)javax.microedition.lcdui.Display.nullGet=true;
            Object app=make("GameMidlet",new Class<?>[0]);statics("GameMidlet");
            if(!(app instanceof Throwable)) {
                if(fault==5)C("k").getField("failStart").setInt(null,1);
                if(fault==6)javax.microedition.lcdui.Display.failSet=1;
                if(fault==7)C("k").getField("failPause").setInt(null,1);
                if(fault==8)javax.microedition.midlet.MIDlet.failNotify=1;
                for(String method:new String[]{"startApp","pauseApp","startApp","pauseApp"}){invoke("GameMidlet",app,method,"()V");statics("GameMidlet");}
                C("k").getField("failDestroy").setInt(null,1);invoke("GameMidlet",app,"destroyApp","(Z)V",false);statics("GameMidlet");
                C("k").getField("failDestroy").setInt(null,0);invoke("GameMidlet",app,"destroyApp","(Z)V",true);statics("GameMidlet");
                invoke("GameMidlet",app,"destroyApp","(Z)V",false);invoke("GameMidlet",app,"startApp","()V");statics("GameMidlet");
                // Multiple instances share the static controller exactly as the original does.
                Object app2=make("GameMidlet",new Class<?>[0]);if(!(app2 instanceof Throwable)){invoke("GameMidlet",app,"destroyApp","(Z)V",true);invoke("GameMidlet",app2,"startApp","()V");statics("GameMidlet");}
            }
            add("midlet:"+javax.microedition.midlet.MIDlet.events);add("display:"+javax.microedition.lcdui.Display.events);events();
        }
    }
    public static void main(String[] args)throws Exception {
        candidate=Boolean.parseBoolean(args[0]);String mode=args[1];
        BufferedReader br=new BufferedReader(new InputStreamReader(WeaponProbe.class.getResourceAsStream("/aliases.tsv"),"UTF-8"));
        String line;while((line=br.readLine())!=null){String[] p=line.split("\t");aliases.put(p[0]+"\t"+p[1]+"\t"+p[2]+"\t"+p[3],p[4]);}br.close();
        digest=MessageDigest.getInstance("SHA-256");
        if(mode.equals("weapon-selection"))selection();else if(mode.equals("weapon-aiming"))aiming();else if(mode.equals("weapon-firing"))firing();
        else if(mode.equals("weapon-update"))projectileUpdate();else if(mode.equals("weapon-drawing"))drawing();
        else if(mode.equals("saucer-motion"))saucerMotion();else if(mode.equals("saucer-reticle"))reticle();else if(mode.equals("saucer-targeting"))targeting();
        else if(mode.equals("saucer-update-draw"))saucerUpdateDraw();else if(mode.equals("midlet-lifecycle"))lifecycle();else throw new AssertionError("Unknown mode");
        StringBuilder hex=new StringBuilder();for(byte b:digest.digest())hex.append(String.format("%02x",b&255));System.out.println(mode+"\t"+calls+"\t"+hex);
        System.err.println("successful="+successes+" expected-or-recorded-exceptions="+failures+" fixture_calls="+fixtureCalls);
        for(Map.Entry<String,long[]> item:outcomes.entrySet())System.err.println("METHOD\t"+item.getKey()+"\t"+item.getValue()[0]+"\t"+item.getValue()[1]);
    }
}
