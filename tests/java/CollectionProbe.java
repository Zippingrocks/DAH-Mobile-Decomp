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
public final class CollectionProbe {
    static boolean candidate;
    static final Map<String,String> aliases = new HashMap<String,String>();
    static final Map<String,Field> fields = new HashMap<String,Field>();
    static final Map<String,Method> methods = new HashMap<String,Method>();
    static MessageDigest digest;
    static long calls, successes, failures, fixtureCalls;
    static final Set<String> TARGETS = new HashSet<String>(Arrays.asList("n","d","r"));
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
    static void decoder(boolean second)throws Exception {set("e",null,"a","B",(byte)0x9a);set("e",null,"a","Z",second);}
    static void events()throws Exception {
        for(String n:new String[]{"b","k","j"})add(n+":"+C(n).getField("events").get(null));
        add("callbacks:"+ProbeEntity.events.toString());add("images:"+Image.calls.toString());
        add("media:"+Manager.calls.toString());
        Object random=get("k",null,"a","Ljava/util/Random;");if(random instanceof FixedRandom)add("rng:"+((FixedRandom)random).count);
    }
    static void clearEvents()throws Exception {
        for(String n:new String[]{"b","k","j"})((StringBuilder)C(n).getField("events").get(null)).setLength(0);
        ProbeEntity.events.setLength(0);Image.reset(0,0);Manager.reset();
    }
    static Graphics graphics()throws Exception {return (Graphics)get("k",null,"a","Ljavax/microedition/lcdui/Graphics;");}
    static void newGraphics(int fail)throws Exception {Graphics g=new Graphics();g.throwAtDraw=fail;set("k",null,"a","Ljavax/microedition/lcdui/Graphics;",g);}
    static Object bucket(int x,int y)throws Exception {Object v=make("n",new Class<?>[]{int.class,int.class},x,y);ok(v);return v;}
    static Vector list(Object group,boolean decoration)throws Exception{return (Vector)get("n",group,decoration?"b":"a","Ljava/util/Vector;");}
    static Object entity(String type,int x,int y,int id)throws Exception {Object v=xyz(type,x,y,id);ok(v);oid(v);return v;}
    static Object addEntity(Object group,String type,int x,int y,int id,boolean decoration)throws Exception {
        Object v=entity(type,x,y,id);set("o",v,"g","Z",decoration);list(group,decoration).add(v);return v;
    }
    static void resources()throws Exception {
        decoder(false);Image.reset(0,0);ok(invoke("s",null,"a","(Ljava/lang/Class;)V",CollectionProbe.class));
        set("a",null,"c","Z",false);set("a",null,"b","Ljava/util/Vector;",new Vector(24));decoder(false);
        ok(invoke("a",null,"a","(Ljava/lang/Class;)V",CollectionProbe.class));ok(invoke("a",null,"a","()V"));
        Object font=make("l",new Class<?>[]{String.class,String.class,String.class},"fnt1","/fnt1.font","/fnt1.def");ok(font);set("k",null,"a","Ll;",font);
        set("c",null,"a","Ljavax/microedition/lcdui/Image;",Image.createImage("/pics/alienWeapons.png"));
        set("b",null,"b","Ljavax/microedition/lcdui/Image;",Image.createImage("/pics/Hud.png"));
        resetWorld();
    }
    static void resetWorld()throws Exception {
        for(String n:new String[]{"a","i","f","p","d"})set("b",null,n,"B",(byte)0);
        for(String n:new String[]{"a","b","c"})set("b",null,n,"S",(short)0);
        set("b",null,"o","B",(byte)16);set("b",null,"s","I",0);set("b",null,"e","I",12345);
        set("b",null,"g","S",(short)256);set("b",null,"f","S",(short)256);set("b",null,"b","B",(byte)0);
        set("b",null,"a","[Lo;",Array.newInstance(C("o"),256));
        C("b").getField("failSelect").setInt(null,0);C("j").getField("failCall").setInt(null,0);C("j").getField("changeHealth").setBoolean(null,false);
        C("b").getField("bucket").set(null,bucket(0,0));
        set("k",null,"a","I",176);set("k",null,"b","I",208);set("k",null,"c","I",50);C("k").getField("inputMask").setInt(null,0);
        set("k",null,"a","Ljava/util/Random;",new FixedRandom(new int[]{7,-1,Integer.MIN_VALUE},-1));
        set("o",null,"n","I",0);set("o",null,"o","I",8);
        Object player=entity("j",30,40,0);set("b",null,"b","Lj;",player);set("b",null,"a","Lj;",player);
        Object fallback=entity("f",30,40,6);set("b",null,"a","Lf;",fallback);
        Object weapon=C("c").newInstance();C("c").getField("m").setInt(weapon,22);set("j",fallback,"a","Lc;",weapon);
        set("j",null,"a","[B",new byte[12]);byte[] max=new byte[12];Arrays.fill(max,(byte)10);set("c",null,"a","[B",max);
        Object sound=make("g",new Class<?>[0]);ok(sound);ok(invoke("g",sound,"a","(I)V",5));
        byte[][] samples=new byte[5][];for(int n=0;n<5;++n)samples[n]=new byte[]{1,2};set("g",sound,"a","[[B",samples);set("k",null,"a","Lg;",sound);
        clearEvents();newGraphics(-1);
    }
    static void world()throws Exception {
        add("transfer:"+get("b",null,"b","B")+":"+value(get("b",null,"a","[Lo;"),0));
        add("hit:"+get("b",null,"e","I")+",score:"+get("b",null,"a","S")+",timer:"+get("b",null,"s","I"));
        add("player:"+entitySig(get("b",null,"b","Lj;")));add("ammo:"+value(get("j",null,"a","[B"),0));events();
    }
    static byte[] bytes(String path)throws Exception {InputStream in=CollectionProbe.class.getResourceAsStream(path);if(in==null)throw new AssertionError(path);ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1)out.write(b,0,n);in.close();return out.toByteArray();}
    static final String[] HOUSE={"data/HousePieces.dat","data/HouseParts.dat","data/Houses.dat"};
    static void resetBuildings(boolean second,boolean loaded)throws Exception {
        set("d",null,"a","[[S",new short[][]{{8,9}});set("d",null,"a","[[[S",new short[][][]{{{1,2}}});set("d",null,"b","[[[S",new short[][][]{{{3}}});
        set("d",null,"a","Z",loaded);set("d",null,"a","[Ljavax/microedition/lcdui/Image;",new Image[2]);decoder(second);
    }
    static void recordBuildingStatics()throws Exception {statics("d");add("decoder:"+get("e",null,"a","B")+":"+get("e",null,"a","Z"));events();}
    static void loadBuildings()throws Exception {
        resetBuildings(false,false);Object result=invoke("d",null,"a","(Ljava/lang/Object;)Z",new BuildingsResourceOwner());
        if(!Boolean.TRUE.equals(result))throw new AssertionError("Real building tables failed");set("d",null,"a","Z",true);
    }
    static void buildingLoad()throws Exception {
        resources();BuildingLoader loader=new BuildingLoader(bytes("/BuildingsResourceOwner.class"));Object owner=loader.owner();
        for(String name:HOUSE)loader.data.put(name,bytes("/"+name));
        for(String name:HOUSE) {
            byte[] original=loader.data.get(name);
            for(int second=0;second<2;second++)for(int cut=-1;cut<=original.length;cut++) {
                resetBuildings(second!=0,(cut&1)!=0);clearEvents();loader.data.put(name,cut<0?null:Arrays.copyOf(original,cut));
                invoke("d",null,"a","(Ljava/lang/Object;)Z",owner);recordBuildingStatics();
            }
            loader.data.put(name,original);
            for(int fail:new int[]{0,1,2,7,30,original.length-1}) {
                resetBuildings(false,true);loader.faultName=name;loader.faultAt=fail;
                invoke("d",null,"a","(Ljava/lang/Object;)Z",owner);recordBuildingStatics();
            }
            loader.faultName=null;
            for(int first:new int[]{128,255,0}) {
                byte[] changed=original.clone();changed[0]=(byte)first;loader.data.put(name,changed);resetBuildings(false,false);
                invoke("d",null,"a","(Ljava/lang/Object;)Z",owner);recordBuildingStatics();
            }
            loader.data.put(name,original);
        }
        resetBuildings(false,true);invoke("d",null,"a","(Ljava/lang/Object;)Z",(Object)null);recordBuildingStatics();
        for(int i=0;i<3;i++){invoke("d",null,"a","(Ljava/lang/Object;)Z",owner);recordBuildingStatics();}
        Image[] images=(Image[])get("d",null,"a","[Ljavax/microedition/lcdui/Image;");images[0]=Image.createImage("/pics/house.png");
        for(int i=0;i<3;i++){invoke("d",null,"b","()V");recordBuildingStatics();}
    }
    static Object house(int id,int x,int y)throws Exception {return make("d",new Class<?>[]{int.class,int.class,int.class},id,x,y);}
    static Object section(Object unused,Object owner,byte part,int x,int y,byte w,byte h)throws Exception {
        return make("r",new Class<?>[]{C("d"),C("d"),byte.class,int.class,int.class,byte.class,byte.class},unused,owner,part,x,y,w,h);
    }
    static void buildingState()throws Exception {
        resources();loadBuildings();short[][][] houses=(short[][][])get("d",null,"b","[[[S");short[][][] parts=(short[][][])get("d",null,"a","[[[S");
        for(int id=-2;id<=houses.length+1;id++)for(int loc:new int[]{-128,0,40,Integer.MAX_VALUE})for(int rv:new int[]{Integer.MIN_VALUE,-1,0,1,Integer.MAX_VALUE}) {
            resetWorld();set("k",null,"a","Ljava/util/Random;",new FixedRandom(new int[]{rv,~rv,rv+1},-1));
            Object house=house(id,loc,loc+3);record(house);events();
            if(!(house instanceof Throwable)){invoke("d",house,"a","()V");record(C("b").getField("bucket").get(null));world();}
        }
        Object owner=house(0,20,30);ok(owner);Object unused=house(1,0,0);ok(unused);
        for(int part=-1;part<=parts.length;part++)for(int dim:new int[]{-128,-17,-1,0,1,15,16,127}) {
            clearEvents();Object piece=section(unused,owner,(byte)part,70,-40,(byte)(dim+1),(byte)dim);record(piece);recordBuildingStatics();
        }
        // Byte narrowing occurs during each maximum update, not just on return.
        short[][] pieces=new short[6][6];for(int i=0;i<6;i++){pieces[i][3]=(short)(i*81-10);pieces[i][4]=(short)(i*91+10);}
        set("d",null,"a","[[S",pieces);
        for(int seed=0;seed<500;seed++) {
            short[][][] p=new short[1][4][3];for(int i=0;i<4;i++){p[0][i][0]=(short)((i+seed)%6);p[0][i][1]=(short)(seed*67+i);p[0][i][2]=(short)(-seed*45+i);}
            set("d",null,"a","[[[S",p);invoke("d",null,"a","(B)B",(byte)0);invoke("d",null,"b","(B)B",(byte)0);
        }
        loadBuildings();
        for(int fault=0;fault<3;fault++){set("k",null,"a","Ljava/util/Random;",new FixedRandom(new int[]{7,-1,9},fault));Object v=house(0,0,0);record(v);events();}
        set("k",null,"a","Ljava/util/Random;",null);record(house(0,0,0));
        resetWorld();set("d",null,"a","[Ljavax/microedition/lcdui/Image;",new Image[2]);Image.reset(0,2);record(house(0,0,0));recordBuildingStatics();
        loadBuildings();Object build=house(0,0,0);ok(build);
        for(int fail=0;fail<=2;fail++){C("b").getField("failSelect").setInt(null,fail);invoke("d",build,"a","()V");record(C("b").getField("bucket").get(null));events();}
    }
    static void buildingDraw()throws Exception {
        resources();loadBuildings();short[][] pieces=(short[][])get("d",null,"a","[[S");short[][][] parts=(short[][][])get("d",null,"a","[[[S");
        Image[] images=(Image[])get("d",null,"a","[Ljavax/microedition/lcdui/Image;");images[0]=Image.createImage("/pics/house.png");images[1]=Image.createImage("/pics/barn.png");
        for(int id=-1;id<=pieces.length;id++)for(int pos:new int[]{-20,50,170,Integer.MAX_VALUE}) {
            newGraphics(-1);invoke("d",null,"a","(III)V",id,pos,30);add(graphics().snapshot());
        }
        Object owner=house(0,30,50);ok(owner);
        for(int id=0;id<parts.length;id++)for(int variant:new int[]{-1,0,1,2,127})for(int drawFail:new int[]{-1,0,1}) {
            byte[] variations={(byte)variant,(byte)variant,(byte)variant};
            newGraphics(drawFail);invoke("d",null,"b","(I[BII)V",id,variations,25,25);add(graphics().snapshot());
            newGraphics(drawFail);invoke("d",null,"a","(I[BII)V",id,variations,25,25);add(graphics().snapshot());
            newGraphics(drawFail);set("d",owner,"a","[B",variations);
            Object piece=section(null,owner,(byte)id,25,25,(byte)30,(byte)40);ok(piece);invoke("r",piece,"g","()V");record(piece);add(graphics().snapshot());
        }
        Object piece=section(owner,null,(byte)0,0,0,(byte)1,(byte)2);ok(piece);newGraphics(-1);invoke("r",piece,"g","()V");add(graphics().snapshot());
        for(byte[] variants:new byte[][]{null,new byte[0],new byte[1]}) {newGraphics(-1);invoke("d",null,"a","(I[BII)V",0,variants,0,0);add(graphics().snapshot());}
    }
    static void collectionMath()throws Exception {
        resources();Random rng=new Random(400071L);
        for(int i=0;i<16000;i++) {
            int[] v=new int[8];for(int j=0;j<8;j++)v[j]=i<8000?rng.nextInt(401)-200:EDGE[rng.nextInt(EDGE.length)];
            Object[] args=new Object[8];for(int j=0;j<8;j++)args[j]=v[j];
            invoke("n",null,"a","(IIIIIIII)Z",args);invoke("n",null,"a","(IIIIIIII)I",args);
        }
        Object left=entity("o",0,0,0),right=entity("o",0,0,37);loadBuildings();Object owner=house(0,0,0);ok(owner);
        Object building=section(null,owner,(byte)0,0,0,(byte)-17,(byte)100);ok(building);
        for(int i=0;i<6000;i++) {
            Object v=i%3==0?building:left;
            for(Object ob:new Object[]{v,right})for(String n:new String[]{"k","l"})set("o",ob,n,"I",i<4000?rng.nextInt(900)-450:EDGE[rng.nextInt(EDGE.length)]);
            for(Object ob:new Object[]{v,right})for(String n:new String[]{"o","p"})set("o",ob,n,"B",(byte)rng.nextInt());
            set("b",null,"b","S",(short)(rng.nextInt(50)-25));set("b",null,"c","S",(short)(rng.nextInt(50)-25));
            set("k",null,"a","I",i%17==0?Integer.MAX_VALUE:176);set("k",null,"b","I",i%19==0?-2:208);
            invoke("n",null,"a","(Lo;)Z",v);invoke("n",null,"a","(Lo;Lo;)Z",v,right);
        }
        invoke("n",null,"a","(Lo;)Z",(Object)null);invoke("n",null,"a","(Lo;Lo;)Z",null,right);
        set("s",null,"b","[B",null);invoke("n",null,"a","(Lo;)Z",left);invoke("n",null,"a","(Lo;Lo;)Z",building,right);
    }
    static void collectionPopulation()throws Exception {
        resources();loadBuildings();
        for(int origin:new int[]{-129,0,127,Integer.MAX_VALUE})for(int type=-128;type<=127;type++) {
            clearEvents();Object group=bucket(origin,origin+1);C("b").getField("bucket").set(null,group);
            invoke("n",group,"a","(BBB)V",(byte)(type+11),(byte)(type-20),(byte)type);record(group);world();
        }
        byte[] data={8,0,1,2,12,3,4,65,5,6,66,7,8,6,9,10,37,11,12,1,0,14,58,15,16};
        for(int cut=0;cut<=data.length;cut++) {
            Object group=bucket(40,70);C("b").getField("bucket").set(null,group);clearEvents();
            DataInputStream in=new DataInputStream(new ByteArrayInputStream(Arrays.copyOf(data,cut)));
            invoke("n",group,"a","(Ljava/io/DataInputStream;)V",in);add("remaining:"+in.available());record(group);events();
        }
        for(int count:new int[]{-128,-1,0,1,127}) {
            Object group=bucket(0,0);byte[] f=data.clone();f[0]=(byte)count;
            invoke("n",group,"a","(Ljava/io/DataInputStream;)V",new DataInputStream(new ByteArrayInputStream(f)));record(group);
        }
        Object group=bucket(0,0);invoke("n",group,"a","(Ljava/io/DataInputStream;)V",(Object)null);
        Random rng=new Random(48572L);ArrayList<Object> objects=new ArrayList<Object>();
        for(int i=0;i<500;i++) {
            Object v=entity("o",i,rng.nextInt(21)-10,37);set("o",v,"p","B",(byte)(i%4));set("o",v,"g","Z",(i%3)==0);
            objects.add(v);invoke("n",group,"a","(Lo;)V",v);record(group);
        }
        for(int i=0;i<80;i++){Object v=objects.get(i);invoke("n",group,"a","(Lo;)V",v);record(group);}
        for(int i=0;i<objects.size();i+=2) {Object v=objects.get(i);invoke("n",group,"b","(Lo;)V",v);record(group);}
        Object v=objects.get(3);set("o",v,"g","Z",!((Boolean)get("o",v,"g","Z")));invoke("n",group,"b","(Lo;)V",v);record(group);
        invoke("n",group,"a","(Lo;)V",(Object)null);invoke("n",group,"b","(Lo;)V",(Object)null);record(group);
        Object bad=bucket(0,0);list(bad,false).add("bad element");invoke("n",bad,"a","(Lo;)V",objects.get(1));record(bad);
        list(bad,false).clear();list(bad,false).add(null);invoke("n",bad,"a","(Lo;)V",objects.get(1));record(bad);
    }
    static Object queryScene(int seed)throws Exception {
        Object group=bucket(0,0);Random rng=new Random(seed*17L+774L);
        addEntity(group,"o",30,40,58,false);addEntity(group,"i",31,40,12,false);
        addEntity(group,"o",34,43,59,false);addEntity(group,"o",37,42,64,false);
        addEntity(group,"j",33,41,0,false);addEntity(group,"j",38,40,2,false);
        addEntity(group,"f",32,42,6,false);
        for(int i=0;i<4;i++) {
            Object v=addEntity(group,"j",rng.nextInt(151)-40,rng.nextInt(151)-40,37,false);
            set("j",v,"g","B",(byte)new int[]{0,15,16,17}[i]);set("j",v,"c","S",(short)(seed%3-1));set("j",v,"e","S",(short)(seed%3-1));
        }
        Object marker=addEntity(group,"m",34,41,65,false);set("m",marker,"a","Lo;",list(group,false).elementAt(4));
        C("b").getField("bucket").set(null,group);return group;
    }
    static void collectionQueries()throws Exception {
        resources();Random rng=new Random(247119L);
        for(int seed=0;seed<650;seed++) {
            resetWorld();Object group=queryScene(seed);Object player=get("b",null,"b","Lj;");
            set("j",player,"b","S",(short)(seed%3-1));clearEvents();
            Object ignore=seed%4==0?null:seed%4==1?player:list(group,false).elementAt(seed%list(group,false).size());
            int x=rng.nextInt(80),y=rng.nextInt(80),x1=x+rng.nextInt(80)-10,y1=y+rng.nextInt(80)-10;
            invoke("n",group,"a","(IIIILo;)Lo;",x,y,x1,y1,ignore);record(group);world();
            invoke("n",group,"b","(IIIILo;)Lo;",x,y,x1,y1,ignore);record(group);
            invoke("n",group,"a","(Lo;)Lo;",ignore);record(group);world();
            invoke("n",group,"c","(IIIILo;)Lo;",x,y,rng.nextInt(100)-50,rng.nextInt(100)-50,ignore);record(group);world();
        }
        // Successful pickup/removal path, rather than only misses and exceptional scenarios.
        resetWorld();Object group=queryScene(4);Object player=get("b",null,"b","Lj;");
        for(int t=0;t<4;t++){invoke("n",group,"a","(IIIILo;)Lo;",-100,-100,500,500,player);record(group);world();}
        // Tie order and building extents in the ray and rectangle routes.
        resetWorld();loadBuildings();group=bucket(0,0);Object build=house(0,0,0);ok(build);
        for(int i=0;i<2;i++){Object part=section(null,build,(byte)0,50,50,(byte)40,(byte)40);ok(part);list(group,false).add(part);}
        Object ignored=entity("j",0,0,0);
        for(int x:new int[]{-1,0,49,50,90,91})for(int y:new int[]{49,50,90,91}) {
            invoke("n",group,"a","(IIIILo;)Lo;",x,y,x,y,ignored);
            invoke("n",group,"c","(IIIILo;)Lo;",x,y,100,0,ignored);world();
        }
        list(group,false).add(null);invoke("n",group,"a","(IIIILo;)Lo;",0,0,100,100,ignored);invoke("n",group,"b","(IIIILo;)Lo;",0,0,100,100,ignored);
        invoke("n",group,"c","(IIIILo;)Lo;",0,0,100,100,ignored);invoke("n",group,"a","(Lo;)Lo;",ignored);
    }
    static void collectionTargeting()throws Exception {
        resources();
        for(int dir=-1;dir<=4;dir++)for(int x:new int[]{-40,0,30,176,177})for(int y:new int[]{-40,0,40,208,209})for(int dead:new int[]{0,15,16,17}) {
            Object group=bucket(0,0);Object source=entity("j",30,40,0);set("j",source,"f","B",(byte)dir);list(group,false).add(source);
            Object target=addEntity(group,"j",x,y,37,false);set("j",target,"g","B",(byte)dead);
            addEntity(group,"j",x+1,y+1,37,false);addEntity(group,"o",30,40,58,false);
            invoke("n",group,"a","(Lj;)Lo;",source);record(group);
        }
        Random rng=new Random(800123L);
        for(int i=0;i<2000;i++) {
            Object group=bucket(0,0);Object source=entity("j",EDGE[i%EDGE.length],EDGE[(i/13)%EDGE.length],0);set("j",source,"f","B",(byte)(i%4));
            for(int j=0;j<3;j++)addEntity(group,"j",EDGE[rng.nextInt(EDGE.length)],EDGE[rng.nextInt(EDGE.length)],37,false);
            invoke("n",group,"a","(Lj;)Lo;",source);
        }
        for(int state:new int[]{0,15,16,17})for(int health:new int[]{-1,0,1,30})for(int range:new int[]{-1,0,1,100,5000})for(int fault:new int[]{0,1,2}) {
            resetWorld();Object group=bucket(0,0);Object source=entity("j",40,40,0);list(group,false).add(source);
            Object target=addEntity(group,"j",42,42,37,false);set("j",target,"g","B",(byte)state);set("j",target,"e","S",(short)health);
            addEntity(group,"f",41,41,6,false);list(group,false).add(null);addEntity(group,"o",40,40,58,false);
            C("j").getField("failCall").setInt(null,fault);C("j").getField("changeHealth").setBoolean(null,true);clearEvents();
            invoke("n",group,"a","(Lo;I)V",source,range);record(group);record(target);world();
        }
        Object group=bucket(0,0);addEntity(group,"j",40,40,37,false);invoke("n",group,"a","(Lo;I)V",null,10);
        invoke("n",group,"a","(Lj;)Lo;",(Object)null);
    }
    static ProbeEntity probe(Object group,int label,int x,int y,boolean deco)throws Exception {
        ProbeEntity v=new ProbeEntity(x,y,37);v.label=label;v.group=group;v.g=deco;oid(v);list(group,deco).add(v);return v;
    }
    static void collectionLifecycle()throws Exception {
        resources();Random rng=new Random(4199L);
        for(int seed=0;seed<400;seed++) {
            resetWorld();Object group=bucket(0,0);clearEvents();
            for(int i=0;i<8;i++) {
                ProbeEntity p=probe(group,i,20+i,10+rng.nextInt(120),false);
                p.action=seed%9==0?1:0;p.dx=seed%7==0?256:seed%7==1?-100:0;p.dy=(seed+i)%5-2;
                if(seed%13==0&&i==3)p.fault=1;
            }
            for(int j=0;j<3;j++) {invoke("n",group,"b","()V");record(group);world();}
            invoke("n",group,"d","()V");record(group);events();
        }
        // Ascending, descending, tied and overflowed bottom keys; each d() is only two sweeps.
        for(int size=0;size<=30;size++) {
            Object group=bucket(0,0);
            for(int i=0;i<size;i++)probe(group,i,0,(size-i)%7,false);
            for(int j=0;j<4;j++){invoke("n",group,"d","()V");record(group);}
        }
        // Integrated real base-entity update and real pickup side effects/removal.
        for(int flags:new int[]{0,1,16,65536})for(int rise:new int[]{0,1,8,16}) {
            resetWorld();Object group=bucket(0,0);C("b").getField("bucket").set(null,group);
            Object token=addEntity(group,"o",40,40,58,false);Object pickup=addEntity(group,"i",45,45,12,false);
            addEntity(group,"o",50,50,37,false);set("o",token,"m","I",flags);set("o",pickup,"m","I",flags);
            set("o",null,"n","I",rise);set("o",null,"o","I",8);clearEvents();
            for(int tick=0;tick<3;tick++){invoke("n",group,"b","()V");record(group);world();}
        }
        for(int count:new int[]{-128,-1,0,1,127})for(int length:new int[]{0,1,128,256}) {
            resetWorld();Object group=bucket(0,0);probe(group,0,-20,40,false);
            set("b",null,"a","[Lo;",Array.newInstance(C("o"),length));set("b",null,"b","B",(byte)count);
            invoke("n",group,"b","()V");record(group);world();
        }
        for(int kind=0;kind<5;kind++) {
            Object group=bucket(0,0);clearEvents();
            ProbeEntity a=probe(group,0,0,0,false),b=probe(group,1,0,0,false),c=probe(group,2,0,0,true);
            if(kind==1)b.fault=3;if(kind==2)a.action=2;if(kind==3)c.fault=3;if(kind==4)list(group,false).add(null);
            invoke("n",group,"c","()V");record(group);events();invoke("n",group,"c","()V");record(group);
        }
        Object group=bucket(0,0);list(group,false).add(null);invoke("n",group,"b","()V");record(group);invoke("n",group,"d","()V");record(group);
    }
    static void collectionDraw()throws Exception {
        resources();loadBuildings();Object build=house(0,0,0);ok(build);
        for(int seed=0;seed<160;seed++) {
            resetWorld();Object group=bucket(0,0);clearEvents();
            for(int i=0;i<6;i++){ProbeEntity p=probe(group,i,i%2==0?30:-500,seed+i*15,i%3==0);if(seed%7==0&&i==4)p.fault=2;}
            Object piece=section(null,build,(byte)0,40,50,(byte)60,(byte)60);ok(piece);list(group,false).add(piece);
            addEntity(group,"o",50,50,37,false);addEntity(group,"i",70,30,12,true);
            newGraphics(seed%5==0?1:-1);invoke("n",group,"a","()V");add(graphics().snapshot());record(group);events();
            newGraphics(-1);invoke("n",group,"b","()I");record(group);
            for(int i=0;i<list(group,false).size()+2;i++){invoke("n",group,"a","()I");record(group);}
            add(graphics().snapshot());events();
        }
        Object group=bucket(0,0);invoke("n",group,"b","()I");invoke("n",group,"a","()I");record(group);
        list(group,false).add(null);invoke("n",group,"b","()I");record(group);
        list(group,true).add(null);invoke("n",group,"a","()V");record(group);
    }
    public static void main(String[] args)throws Exception {
        candidate=Boolean.parseBoolean(args[0]);String mode=args[1];
        BufferedReader br=new BufferedReader(new InputStreamReader(CollectionProbe.class.getResourceAsStream("/aliases.tsv"),"UTF-8"));
        String line;while((line=br.readLine())!=null){String[] p=line.split("\t");aliases.put(p[0]+"\t"+p[1]+"\t"+p[2]+"\t"+p[3],p[4]);}br.close();
        digest=MessageDigest.getInstance("SHA-256");
        if(mode.equals("building-load"))buildingLoad();else if(mode.equals("building-state"))buildingState();else if(mode.equals("building-draw"))buildingDraw();
        else if(mode.equals("collection-math"))collectionMath();else if(mode.equals("collection-population"))collectionPopulation();
        else if(mode.equals("collection-queries"))collectionQueries();else if(mode.equals("collection-targeting"))collectionTargeting();
        else if(mode.equals("collection-lifecycle"))collectionLifecycle();else if(mode.equals("collection-draw"))collectionDraw();else throw new AssertionError("Unknown mode");
        StringBuilder hex=new StringBuilder();for(byte b:digest.digest())hex.append(String.format("%02x",b&255));
        System.out.println(mode+"\t"+calls+"\t"+hex);
        System.err.println("successful="+successes+" expected-or-recorded-exceptions="+failures+" fixture_calls="+fixtureCalls);
        for(Map.Entry<String,long[]> item:outcomes.entrySet())System.err.println("METHOD\t"+item.getKey()+"\t"+item.getValue()[0]+"\t"+item.getValue()[1]);
    }
    static final class FixedRandom extends Random {
        final int[] values;final int fault;int count;
        FixedRandom(int[] values,int fault){this.values=values;this.fault=fault;}
        public int nextInt(){int index=count++;if(index==fault)throw new IllegalStateException("scripted rng");return values[index%values.length];}
    }
    static final class BuildingLoader extends ClassLoader {
        final byte[] ownerBytes;final Map<String,byte[]> data=new HashMap<String,byte[]>();String faultName;int faultAt;
        BuildingLoader(byte[] bytes){super(CollectionProbe.class.getClassLoader());ownerBytes=bytes;}
        Object owner()throws Exception {Class<?> type=defineClass("BuildingsResourceOwner",ownerBytes,0,ownerBytes.length);Constructor<?> ct=type.getDeclaredConstructor();ct.setAccessible(true);return ct.newInstance();}
        public InputStream getResourceAsStream(String name) {
            final byte[] raw=data.get(name);if(raw==null)return null;final int fail=name.equals(faultName)?faultAt:-1;
            return new InputStream(){int pos;public int read()throws IOException {if(pos==fail)throw new IOException("scripted read");return pos<raw.length?raw[pos++]&255:-1;}};
        }
    }
}
/** Authored resource-owner identity for Class.getResourceAsStream failure scenarios. */
final class BuildingsResourceOwner { }
/** Authored callback/movement record, NOT an original actor implementation. */
final class ProbeEntity extends o {
    static StringBuilder events=new StringBuilder();
    int label,dx,dy,action,fault;Object group;
    ProbeEntity(int x,int y,int id){super(x,y,id);}
    public void f(){events.append("update:"+label+";");if(fault==1)throw new IllegalStateException("scripted update");k+=dx;l+=dy;
        if(action==1)try{CollectionProbe.list(group,g).remove(this);}catch(Exception e){throw new AssertionError(e);}}
    public void g(){events.append("draw:"+label+";");if(fault==2)throw new IllegalStateException("scripted draw");}
    public void a(){events.append("cleanup:"+label+";");if(fault==3)throw new IllegalStateException("scripted cleanup");
        if(action==2)try{CollectionProbe.list(group,g).remove(this);}catch(Exception e){throw new AssertionError(e);}}
}
