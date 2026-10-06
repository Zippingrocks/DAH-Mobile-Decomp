import java.lang.reflect.*;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class MissionStressProbe {
    static Field fieldByTypeOrdinal(Class<?> c,Class<?> type,boolean statik,int ordinal){
        int n=0;
        for(Field f:c.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())==statik&&f.getType()==type){
            if(n++==ordinal){f.setAccessible(true);return f;}
        }
        throw new IllegalStateException("field ordinal");
    }
    static Field staticFieldByTypeName(Class<?>c,String name){
        for(Field f:c.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType().getName().equals(name)){f.setAccessible(true);return f;}
        throw new IllegalStateException("field type "+name);
    }
    static Method method(Class<?>c,String name,Class<?>...params)throws Exception{
        Method m=c.getDeclaredMethod(name,params);m.setAccessible(true);return m;
    }
    static void seed(Class<?> k)throws Exception{
        for(Field f:k.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType()==Random.class){
            f.setAccessible(true);f.set(null,new Random(123456789L));
        }
    }
    static String sha(String text)throws Exception{
        byte[] d=MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8));
        StringBuilder out=new StringBuilder();for(byte b:d)out.append(String.format("%02x",b&255));return out.toString();
    }
    public static void main(String[]args)throws Exception{
        int mission=Integer.parseInt(args[0]);
        int frames=Integer.parseInt(args.length>1?args[1]:"300");
        if(mission<1||mission>13)throw new IllegalArgumentException("mission");

        javax.microedition.lcdui.Image.reset(0,0);
        javax.microedition.media.Manager.reset();
        javax.microedition.rms.RecordStore.reset();

        GameMidlet midlet=new GameMidlet();
        Object controller=staticFieldByTypeName(GameMidlet.class,"k").get(null);
        Class<?> k=controller.getClass();
        seed(k);
        method(k,"i").invoke(controller);
        seed(k);

        Object world=staticFieldByTypeName(k,"b").get(null);
        Class<?> b=world.getClass();
        fieldByTypeOrdinal(b,byte.class,true,15).setByte(null,(byte)(mission-1));

        method(k,"g").invoke(null);
        seed(k);

        Method tick=method(k,"j");
        Method keyPressed=method(k,"keyPressed",int.class);
        Method keyReleased=method(k,"keyReleased",int.class);

        int[] keys={52,54,50,56,53,35,42,48};
        StringBuilder checkpoints=new StringBuilder();
        for(int frame=1;frame<=frames;frame++){
            int key=keys[(frame/17)%keys.length];
            if(frame%17==1)keyPressed.invoke(controller,key);
            if(frame%17==8)keyReleased.invoke(controller,key);
            tick.invoke(controller);
            if(frame%100==0){
                checkpoints.append(frame).append(':')
                    .append(StateProbe.hex(StateProbe.state())).append(';');
            }
        }

        String state="m="+mission+
            ",frames="+frames+
            ",mode="+fieldByTypeOrdinal(k,byte.class,true,0).getByte(null)+
            ",state="+StateProbe.hex(StateProbe.state())+
            ",check="+sha(checkpoints.toString())+
            ",images="+sha(javax.microedition.lcdui.Image.calls.toString())+
            ",media="+sha(javax.microedition.media.Manager.calls.toString());
        System.out.println(state);
        System.out.println("sha="+sha(state));
        midlet.destroyApp(true);
    }
}
