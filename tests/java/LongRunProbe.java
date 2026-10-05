import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
public final class LongRunProbe {
  static Method m(Class<?>c,String n,Class<?>...p)throws Exception{Method x=c.getDeclaredMethod(n,p);x.setAccessible(true);return x;}
  static Field controllerField(){for(Field f:GameMidlet.class.getDeclaredFields())if(f.getType().getName().equals("k"))return f;throw new IllegalStateException();}
  static Field clockField(Class<?>c)throws Exception{for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType()==long.class){f.setAccessible(true);return f;}throw new IllegalStateException();}
  static Field uiField(Class<?>c)throws Exception{for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType().getName().equals("p")){f.setAccessible(true);return f;}throw new IllegalStateException();}
  static Field uiClock(Class<?>c)throws Exception{for(Field f:c.getDeclaredFields())if(!Modifier.isStatic(f.getModifiers())&&f.getType()==long.class){f.setAccessible(true);return f;}throw new IllegalStateException();}
  static String hex(String s)throws Exception{byte[]d=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));StringBuilder b=new StringBuilder();for(byte x:d)b.append(String.format("%02x",x&255));return b.toString();}
  public static void main(String[]args)throws Exception{
    javax.microedition.lcdui.Image.reset(0,0);javax.microedition.media.Manager.reset();javax.microedition.rms.RecordStore.reset();
    GameMidlet gm=new GameMidlet();Field cf=controllerField();cf.setAccessible(true);Object ctl=cf.get(null);Class<?>kc=ctl.getClass();StateProbe.seedRandom();m(kc,"i").invoke(ctl);StateProbe.seedRandom();
    Method tick=m(kc,"j"),paint=m(kc,"paint",javax.microedition.lcdui.Graphics.class),kp=m(kc,"keyPressed",int.class),kr=m(kc,"keyReleased",int.class);
    Field clock=clockField(kc);Object ui=uiField(kc).get(null);Field uic=uiClock(ui.getClass());long sim=10000;javax.microedition.lcdui.Graphics g=new javax.microedition.lcdui.Graphics();
    clock.setLong(null,sim);tick.invoke(ctl);paint.invoke(ctl,g);uic.setLong(ui,0L);
    for(int i=0;i<10;i++){clock.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);}
    for(int action=0;action<9;action++){kp.invoke(ctl,-6);clock.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);kr.invoke(ctl,-6);clock.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);for(int i=0;i<10;i++){clock.setLong(null,sim+=1000);tick.invoke(ctl);paint.invoke(ctl,g);}}
    System.out.println("START="+StateProbe.hex(StateProbe.state()));
    int[] keys={52,54,50,56,53,35,42,48};
    for(int frame=1;frame<=500;frame++){
      int key=keys[(frame/17)%keys.length];
      if(frame%17==1)kp.invoke(ctl,key);
      if(frame%17==8)kr.invoke(ctl,key);
      clock.setLong(null,sim+=100);tick.invoke(ctl);paint.invoke(ctl,g);
      if(frame%100==0)System.out.println("S"+frame+"="+StateProbe.hex(StateProbe.state()));
    }
    System.out.println("FRAME="+hex(g.snapshot()));
    System.out.println("IMAGES="+hex(javax.microedition.lcdui.Image.calls.toString()));
    System.out.println("MEDIA="+hex(javax.microedition.media.Manager.calls.toString()));
    System.out.println("RMS="+hex(javax.microedition.rms.RecordStore.events.toString()));
    gm.destroyApp(true);
  }
}
