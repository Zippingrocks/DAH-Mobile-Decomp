import java.lang.reflect.*;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class MissionFuzzProbe {
    static Field fieldByTypeOrdinal(Class<?> c,Class<?> type,boolean statik,int ordinal){
        int n=0;
        for(Field f:c.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())==statik&&f.getType()==type){
            if(n++==ordinal){f.setAccessible(true);return f;}
        }
        throw new IllegalStateException("field ordinal");
    }
    static Field staticFieldByTypeName(Class<?> c,String name){
        for(Field f:c.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType().getName().equals(name)){
            f.setAccessible(true);return f;
        }
        throw new IllegalStateException("field type "+name);
    }
    static Method method(Class<?> c,String name,Class<?>...params)throws Exception{
        Method m=c.getDeclaredMethod(name,params);m.setAccessible(true);return m;
    }
    static void seedGame(Class<?> k,long seed)throws Exception{
        for(Field f:k.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType()==Random.class){
            f.setAccessible(true);f.set(null,new Random(seed));
        }
    }
    static String sha(String text)throws Exception{
        byte[] d=MessageDigest.getInstance("SHA-256").digest(text.getBytes(StandardCharsets.UTF_8));
        StringBuilder out=new StringBuilder();for(byte b:d)out.append(String.format("%02x",b&255));return out.toString();
    }
    public static void main(String[]args)throws Exception{
        int mission=Integer.parseInt(args[0]);
        int frames=Integer.parseInt(args[1]);
        long seed=Long.parseLong(args[2]);

        javax.microedition.lcdui.Image.reset(0,0);
        javax.microedition.media.Manager.reset();
        javax.microedition.rms.RecordStore.reset();

        GameMidlet midlet=new GameMidlet();
        Object controller=staticFieldByTypeName(GameMidlet.class,"k").get(null);
        Class<?> k=controller.getClass();

        seedGame(k,seed);
        method(k,"i").invoke(controller);
        seedGame(k,seed);

        Object world=staticFieldByTypeName(k,"b").get(null);
        Class<?> b=world.getClass();
        fieldByTypeOrdinal(b,byte.class,true,15).setByte(null,(byte)(mission-1));

        method(k,"g").invoke(null);
        seedGame(k,seed);

        Method tick=method(k,"j");
        Method press=method(k,"keyPressed",int.class);
        Method release=method(k,"keyReleased",int.class);

        int[] keys={52,54,50,56,53,35,42,48,-6,-7};
        boolean[] held=new boolean[keys.length];
        Random input=new Random(seed^0x5DEECE66DL);
        StringBuilder checkpoints=new StringBuilder();

        for(int frame=1;frame<=frames;frame++){
            int op=input.nextInt(5);
            int index=input.nextInt(keys.length);
            if(op==1&&!held[index]){
                press.invoke(controller,keys[index]);
                held[index]=true;
            } else if(op==2&&held[index]){
                release.invoke(controller,keys[index]);
                held[index]=false;
            } else if(op==3){
                for(int i=0;i<held.length;i++) if(held[i]){
                    release.invoke(controller,keys[i]);
                    held[i]=false;
                }
            }
            tick.invoke(controller);
            if(frame%50==0){
                checkpoints.append(frame).append(':')
                    .append(StateProbe.hex(StateProbe.state())).append(';');
            }
        }

        for(int i=0;i<held.length;i++) if(held[i]) release.invoke(controller,keys[i]);

        String state="m="+mission+
            ",frames="+frames+
            ",seed="+seed+
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
