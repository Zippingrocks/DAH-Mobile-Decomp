import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
public final class DeepIntegrationProbe {
  static Method m(Class<?> c,String n,Class<?>...p)throws Exception{Method x=c.getDeclaredMethod(n,p);x.setAccessible(true);return x;}
  static Field controllerField(){for(Field f:GameMidlet.class.getDeclaredFields())if(f.getType().getName().equals("k"))return f;throw new IllegalStateException();}
  static Field staticLong(Class<?> c){for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType()==long.class){f.setAccessible(true);return f;}throw new IllegalStateException("static long");}
  static Field staticP(Class<?> c){for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType().getName().equals("p")){f.setAccessible(true);return f;}throw new IllegalStateException("static p");}
  static Field instanceLong(Class<?> c){for(Field f:c.getDeclaredFields())if(!Modifier.isStatic(f.getModifiers())&&f.getType()==long.class){f.setAccessible(true);return f;}throw new IllegalStateException("instance long");}
  static byte mode(Class<?> c)throws Exception{for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType()==byte.class){f.setAccessible(true);return f.getByte(null);}throw new IllegalStateException("mode byte");}
  static String hex(String s)throws Exception{byte[]d=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));StringBuilder b=new StringBuilder();for(byte x:d)b.append(String.format("%02x",x&255));return b.toString();}
  public static void main(String[]args)throws Exception{
    javax.microedition.lcdui.Image.reset(0,0);javax.microedition.media.Manager.reset();
    GameMidlet gm=new GameMidlet();Field cf=controllerField();cf.setAccessible(true);Object ctl=cf.get(null);Class<?> kc=ctl.getClass();
    StateProbe.seedRandom();m(kc,"i").invoke(ctl);StateProbe.seedRandom();
    Method tick=m(kc,"j"),paint=m(kc,"paint",javax.microedition.lcdui.Graphics.class),kp=m(kc,"keyPressed",int.class),kr=m(kc,"keyReleased",int.class);
    Field klong=staticLong(kc);Object ui=staticP(kc).get(null);Field plong=instanceLong(ui.getClass()); long sim=10000;
    javax.microedition.lcdui.Graphics g=new javax.microedition.lcdui.Graphics();
    klong.setLong(null,sim);tick.invoke(ctl);paint.invoke(ctl,g);plong.setLong(ui,0L);
    for(int i=0;i<10;i++){klong.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);}
    System.out.println("MENU0="+StateProbe.hex(StateProbe.state()));
    for(int action=0;action<9;action++){
      kp.invoke(ctl,-6);klong.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);
      kr.invoke(ctl,-6);klong.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);
      for(int i=0;i<10;i++){klong.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);}
    }
    System.out.println("GAME0="+StateProbe.hex(StateProbe.state()));
    System.out.println("MODE="+mode(kc));
    int[] keys={52,54,50,56,53,52,54};
    for(int key:keys){
      kp.invoke(ctl,key);for(int i=0;i<3;i++){klong.setLong(null,sim+=100);tick.invoke(ctl);paint.invoke(ctl,g);}kr.invoke(ctl,key);
      klong.setLong(null,sim+=100);tick.invoke(ctl);paint.invoke(ctl,g);
    }
    for(int i=0;i<20;i++){klong.setLong(null,sim+=100);tick.invoke(ctl);paint.invoke(ctl,g);}
    System.out.println("GAME1="+StateProbe.hex(StateProbe.state()));
    System.out.println("FRAME="+hex(g.snapshot()));
    System.out.println("IMAGES="+hex(javax.microedition.lcdui.Image.calls.toString()));
    System.out.println("MEDIA="+hex(javax.microedition.media.Manager.calls.toString()));
    gm.destroyApp(true);
  }
}
