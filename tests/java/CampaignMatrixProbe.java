import java.lang.reflect.*;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.util.Random;

public final class CampaignMatrixProbe {
    static Field fieldByTypeOrdinal(Class<?> c, Class<?> type, boolean statik, int ordinal) {
        int n=0;
        for (Field f:c.getDeclaredFields()) {
            if (Modifier.isStatic(f.getModifiers())==statik && f.getType()==type) {
                if (n++==ordinal) { f.setAccessible(true); return f; }
            }
        }
        throw new IllegalStateException("field ordinal "+type+" "+ordinal);
    }
    static Field staticFieldByTypeName(Class<?> c,String name) {
        for(Field f:c.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType().getName().equals(name)){f.setAccessible(true);return f;}
        throw new IllegalStateException("static field type "+name);
    }
    static Method method(Class<?> c,String name,boolean statik,Class<?> ret,Class<?>...params) {
        for(Method m:c.getDeclaredMethods()) if(m.getName().equals(name)&&Modifier.isStatic(m.getModifiers())==statik&&m.getReturnType()==ret&&java.util.Arrays.equals(m.getParameterTypes(),params)){m.setAccessible(true);return m;}
        throw new IllegalStateException("method "+name);
    }
    static Method completionMethod(Class<?> c) {
        for(String name:new String[]{"boolean_b","b"}) {
            for(Method m:c.getDeclaredMethods()) if(m.getName().equals(name)&&Modifier.isStatic(m.getModifiers())&&m.getReturnType()==boolean.class&&m.getParameterTypes().length==0){m.setAccessible(true);return m;}
        }
        throw new IllegalStateException("completion method");
    }
    static String sha(String s)throws Exception{byte[]d=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));StringBuilder b=new StringBuilder();for(byte x:d)b.append(String.format("%02x",x&255));return b.toString();}
    static void seedRandom(Class<?> k)throws Exception{
        for(Field f:k.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType()==Random.class){f.setAccessible(true);f.set(null,new Random(123456789L));}
    }
    static void satisfy(Class<?> b,int kind,int target)throws Exception{
        byte[] kills=(byte[])fieldByTypeOrdinal(b,byte[].class,true,1).get(null);
        byte[] abduct=(byte[])fieldByTypeOrdinal(b,byte[].class,true,2).get(null);
        switch(kind){
            case 0:kills[0]=(byte)target;break;
            case 1:kills[1]=(byte)target;break;
            case 2:fieldByTypeOrdinal(b,byte.class,true,5).setByte(null,(byte)target);break;
            case 3:fieldByTypeOrdinal(b,byte.class,true,6).setByte(null,(byte)target);break;
            case 4:kills[0]=(byte)target;break;
            case 5:abduct[0]=(byte)target;break;
            case 6:abduct[1]=(byte)target;break;
            case 7:abduct[2]=(byte)target;break;
            case 8:abduct[3]=(byte)target;break;
            case 9:fieldByTypeOrdinal(b,byte.class,true,7).setByte(null,(byte)target);break;
            case 10:abduct[0]=(byte)target;break;
            case 11:kills[0]=(byte)target;break;
            case 12:fieldByTypeOrdinal(b,byte.class,true,8).setByte(null,(byte)target);break;
            default:throw new IllegalArgumentException("kind "+kind);
        }
    }
    public static void main(String[]args)throws Exception{
        int mission=Integer.parseInt(args[0]); if(mission<1||mission>13)throw new IllegalArgumentException("mission");
        Class<?> gm=Class.forName("GameMidlet");Object midlet=gm.getDeclaredConstructor().newInstance();
        Field controllerField=staticFieldByTypeName(gm,"k");Object ctl=controllerField.get(null);Class<?> k=ctl.getClass();
        seedRandom(k);Method init=method(k,"i",false,void.class);init.invoke(ctl);seedRandom(k);
        Field worldField=staticFieldByTypeName(k,"b");Object world=worldField.get(null);Class<?> b=world.getClass();
        Class<?> sprite=Class.forName("s");Method spriteLoad=method(sprite,"a",true,void.class,Class.class);spriteLoad.invoke(null,k);
        Field missionField=fieldByTypeOrdinal(b,byte.class,true,15);missionField.setByte(null,(byte)(mission-1));
        Method load=method(b,"e",false,void.class);load.invoke(world);
        byte[] table=(byte[])fieldByTypeOrdinal(b,byte[].class,true,0).get(null);int off=(mission-1)*4;
        int kind=table[off]&255, authored=table[off+1]&255, mode=table[off+2]&255, map=table[off+3]&255;
        int runtimeTarget=fieldByTypeOrdinal(b,int.class,true,13).getInt(null);
        int dynamicTotal=fieldByTypeOrdinal(b,int.class,true,12).getInt(null);
        Method done=completionMethod(b);boolean initial=((Boolean)done.invoke(null)).booleanValue();
        satisfy(b,kind,runtimeTarget);boolean complete=((Boolean)done.invoke(null)).booleanValue();
        int progress=fieldByTypeOrdinal(b,int.class,true,14).getInt(null);
        String state="m="+mission+",kind="+kind+",authored="+authored+",mode="+mode+",map="+map+",target="+runtimeTarget+",dynamic="+dynamicTotal+",initial="+initial+",complete="+complete+",progress="+progress;
        System.out.println(state);
        System.out.println("sha="+sha(state));
    }
}
