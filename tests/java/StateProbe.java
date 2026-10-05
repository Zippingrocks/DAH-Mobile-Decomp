import java.lang.reflect.*;
import java.util.*;
import java.security.*;
import java.nio.charset.StandardCharsets;
public final class StateProbe {
  static final Set<String> GAME=new HashSet<String>(); static {GAME.add("GameMidlet");for(char c='a';c<='t';c++)GAME.add(String.valueOf(c));}
  static IdentityHashMap<Object,Integer> seen; static StringBuilder out;
  static String hex(String s)throws Exception{byte[]d=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));StringBuilder b=new StringBuilder();for(byte x:d)b.append(String.format("%02x",x&255));return b.toString();}
  static boolean game(Class<?> c){return c!=null&&GAME.contains(c.getName());}
  static String desc(Class<?> t){if(t.isPrimitive()){if(t==int.class)return"I";if(t==byte.class)return"B";if(t==short.class)return"S";if(t==long.class)return"J";if(t==boolean.class)return"Z";if(t==char.class)return"C";if(t==float.class)return"F";if(t==double.class)return"D";return"V";}if(t.isArray())return t.getName().replace('.','/');return"L"+t.getName().replace('.','/')+";";}
  static Object normalized(Field f,Object v,int longOrdinal){if(f.getType()==long.class){String c=f.getDeclaringClass().getName();if(c.equals("j")||c.equals("k")||c.equals("p")||(c.equals("a")&&longOrdinal==0))return Long.valueOf(0);}return v;}
  static void value(Object v)throws Exception{
    if(v==null){out.append("null;");return;}Class<?> c=v.getClass();
    if(c==String.class||v instanceof Number||v instanceof Boolean||v instanceof Character){out.append(v).append(';');return;}
    if(c.isArray()){int n=Array.getLength(v);out.append("arr[").append(n).append("]{");for(int i=0;i<n;i++)value(Array.get(v,i));out.append("};");return;}
    if(v instanceof Vector){Vector<?> q=(Vector<?>)v;out.append("vec[").append(q.size()).append("]{");for(Object x:q)value(x);out.append("};");return;}
    if(c.getName().equals("javax.microedition.lcdui.Image")){try{Field p=c.getField("path");out.append("img:").append(p.get(v)).append(';');}catch(Exception e){out.append("img;");}return;}
    if(v instanceof java.util.Random){out.append("Random;");return;}
    if(v instanceof Thread){out.append("Thread;");return;}
    if(!game(c)){out.append("ext:").append(c.getName()).append(';');return;}
    Integer id=seen.get(v);if(id!=null){out.append("ref#").append(id).append(';');return;}id=seen.size();seen.put(v,id);out.append("obj#").append(id).append(':').append(c.getName()).append('{');
    ArrayList<Class<?>> chain=new ArrayList<Class<?>>();for(Class<?> q=c;game(q);q=q.getSuperclass())chain.add(q);Collections.reverse(chain);
    for(Class<?> q:chain){int li=0;for(Field f:q.getDeclaredFields()){if(Modifier.isStatic(f.getModifiers()))continue;f.setAccessible(true);out.append(desc(f.getType())).append('=');Object x=f.get(v);x=normalized(f,x,f.getType()==long.class?li:-1);if(f.getType()==long.class)li++;value(x);}}
    out.append("};");
  }
  static String state()throws Exception{seen=new IdentityHashMap<Object,Integer>();out=new StringBuilder();for(String name:new TreeSet<String>(GAME)){Class<?> c=Class.forName(name);out.append("CLASS:").append(name).append('{');int li=0;for(Field f:c.getDeclaredFields()){if(!Modifier.isStatic(f.getModifiers()))continue;f.setAccessible(true);out.append(desc(f.getType())).append('=');Object x=f.get(null);x=normalized(f,x,f.getType()==long.class?li:-1);if(f.getType()==long.class)li++;value(x);}out.append("}\n");}return out.toString();}
  static Field ctlField(){for(Field f:GameMidlet.class.getDeclaredFields())if(f.getType().getName().equals("k"))return f;throw new RuntimeException();}
  static void seedRandom()throws Exception{Class<?> c=Class.forName("k");for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType()==java.util.Random.class){f.setAccessible(true);f.set(null,new java.util.Random(123456789L));}}
  static Method method(Class<?> c,String n,Class<?>...p)throws Exception{Method m=c.getDeclaredMethod(n,p);m.setAccessible(true);return m;}
  public static void main(String[]args)throws Exception{
    javax.microedition.lcdui.Image.reset(0,0);javax.microedition.media.Manager.reset();GameMidlet m=new GameMidlet();Field cf=ctlField();cf.setAccessible(true);Object ctl=cf.get(null);Class<?> kc=ctl.getClass();seedRandom();method(kc,"i").invoke(ctl);seedRandom();
    System.out.println("S0="+hex(state()));
    Method tick=method(kc,"j"),kp=method(kc,"keyPressed",int.class),kr=method(kc,"keyReleased",int.class);
    for(int i=0;i<5;i++)tick.invoke(ctl);System.out.println("S5="+hex(state()));
    int[] keys={1,2,5,6,8,9,10,11,12,35,42,-6,-7};
    for(int key:keys){kp.invoke(ctl,key);tick.invoke(ctl);kr.invoke(ctl,key);tick.invoke(ctl);}System.out.println("SK="+hex(state()));
    javax.microedition.lcdui.Graphics g=new javax.microedition.lcdui.Graphics();method(kc,"paint",javax.microedition.lcdui.Graphics.class).invoke(ctl,g);System.out.println("PX="+hex(g.snapshot()));
    m.destroyApp(true);
  }
}
