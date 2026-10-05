import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
public final class IntegrationProbe {
  static String hex(String s) throws Exception { byte[] d=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));StringBuilder b=new StringBuilder();for(byte x:d)b.append(String.format("%02x",x&255));return b.toString(); }
  static Field controllerField() { for(Field f:GameMidlet.class.getDeclaredFields()) if(f.getType().getName().equals("k")) return f; throw new IllegalStateException(); }
  static Field startGuard(Class<?> c) throws Exception {
    try { Field f=c.getDeclaredField("var_boolean_i"); if(f.getType()==boolean.class)return f; } catch(NoSuchFieldException ignored){}
    Field f=c.getDeclaredField("i"); if(f.getType()!=boolean.class)throw new IllegalStateException("wrong i"); return f;
  }
  public static void main(String[] args) throws Exception {
    javax.microedition.lcdui.Image.reset(0,0); javax.microedition.media.Manager.reset();
    javax.microedition.lcdui.Display.events.setLength(0); javax.microedition.midlet.MIDlet.events.setLength(0);
    GameMidlet m=new GameMidlet(); Field cf=controllerField();cf.setAccessible(true);Object ctl=cf.get(null);Class<?> kc=ctl.getClass();
    Method init=kc.getDeclaredMethod("i");init.setAccessible(true);init.invoke(ctl);
    Method tick=kc.getDeclaredMethod("j");tick.setAccessible(true); for(int i=0;i<5;i++)tick.invoke(ctl);
    javax.microedition.lcdui.Graphics g=new javax.microedition.lcdui.Graphics();
    Method paint=kc.getDeclaredMethod("paint",javax.microedition.lcdui.Graphics.class);paint.setAccessible(true);paint.invoke(ctl,g);
    Field guard=startGuard(kc);guard.setAccessible(true);guard.setBoolean(ctl,true);
    m.startApp();m.pauseApp();m.destroyApp(true);
    System.out.println("images="+javax.microedition.lcdui.Image.calls.size()+":"+hex(javax.microedition.lcdui.Image.calls.toString()));
    System.out.println("media="+javax.microedition.media.Manager.calls.size()+":"+hex(javax.microedition.media.Manager.calls.toString()));
    System.out.println("display="+hex(javax.microedition.lcdui.Display.events.toString()));
    System.out.println("midlet="+hex(javax.microedition.midlet.MIDlet.events.toString()));
    System.out.println("paint="+hex(g.snapshot()));
  }
}
