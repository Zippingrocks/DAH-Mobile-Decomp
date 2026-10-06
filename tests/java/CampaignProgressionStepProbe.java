import java.lang.reflect.*;
import java.security.MessageDigest;
import java.util.*;

public final class CampaignProgressionStepProbe {
    static Field fieldByTypeOrdinal(Class<?> c, Class<?> type, boolean statik, int ordinal) {
        int n=0;
        for(Field f:c.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())==statik&&f.getType()==type) {
            if(n++==ordinal){f.setAccessible(true);return f;}
        }
        throw new IllegalStateException("field ordinal");
    }
    static Field staticFieldByTypeName(Class<?> c,String name) {
        for(Field f:c.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType().getName().equals(name)){f.setAccessible(true);return f;}
        throw new IllegalStateException("static field type "+name);
    }
    static Method method(Class<?> c,String name,boolean statik,Class<?> ret,Class<?>...params) {
        for(Method m:c.getDeclaredMethods()) if(m.getName().equals(name)&&Modifier.isStatic(m.getModifiers())==statik&&m.getReturnType()==ret&&Arrays.equals(m.getParameterTypes(),params)){m.setAccessible(true);return m;}
        throw new IllegalStateException("method "+name);
    }
    static Method completionMethod(Class<?> c) {
        for(String name:new String[]{"boolean_b","b"}) for(Method m:c.getDeclaredMethods())
            if(m.getName().equals(name)&&Modifier.isStatic(m.getModifiers())&&m.getReturnType()==boolean.class&&m.getParameterTypes().length==0){m.setAccessible(true);return m;}
        throw new IllegalStateException("completion method");
    }
    static String sha(byte[] data)throws Exception {
        byte[] digest=MessageDigest.getInstance("SHA-256").digest(data);
        StringBuilder out=new StringBuilder();for(byte value:digest)out.append(String.format("%02x",value&255));return out.toString();
    }
    static void seedRandom(Class<?> k)throws Exception {
        for(Field f:k.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType()==Random.class){f.setAccessible(true);f.set(null,new Random(123456789L));}
    }
    static void satisfy(Class<?> b,int kind,int target)throws Exception {
        byte[] kills=(byte[])fieldByTypeOrdinal(b,byte[].class,true,1).get(null);
        byte[] abduct=(byte[])fieldByTypeOrdinal(b,byte[].class,true,2).get(null);
        switch(kind){
            case 0:kills[0]=(byte)target;break; case 1:kills[1]=(byte)target;break;
            case 2:fieldByTypeOrdinal(b,byte.class,true,5).setByte(null,(byte)target);break;
            case 3:fieldByTypeOrdinal(b,byte.class,true,6).setByte(null,(byte)target);break;
            case 4:kills[0]=(byte)target;break; case 5:abduct[0]=(byte)target;break;
            case 6:abduct[1]=(byte)target;break; case 7:abduct[2]=(byte)target;break;
            case 8:abduct[3]=(byte)target;break;
            case 9:fieldByTypeOrdinal(b,byte.class,true,7).setByte(null,(byte)target);break;
            case 10:abduct[0]=(byte)target;break; case 11:kills[0]=(byte)target;break;
            case 12:fieldByTypeOrdinal(b,byte.class,true,8).setByte(null,(byte)target);break;
            default:throw new IllegalArgumentException("kind "+kind);
        }
    }
    static byte[] saveBuffer(Class<?> k)throws Exception {
        for(Field f:k.getDeclaredFields()) if(Modifier.isStatic(f.getModifiers())&&f.getType()==byte[].class){
            f.setAccessible(true);byte[] value=(byte[])f.get(null);if(value!=null&&value.length==82)return value;
        }
        throw new IllegalStateException("82-byte save buffer");
    }
    public static void main(String[] args)throws Exception {
        int expected=Integer.parseInt(args[0]);
        Class<?> gm=Class.forName("GameMidlet");Object midlet=gm.getDeclaredConstructor().newInstance();
        Object controller=staticFieldByTypeName(gm,"k").get(null);Class<?> k=controller.getClass();
        seedRandom(k);method(k,"i",false,void.class).invoke(controller);seedRandom(k);
        Object world=staticFieldByTypeName(k,"b").get(null);Class<?> b=world.getClass();
        Method load;try{load=method(b,"void_a",false,void.class);}catch(Exception ex){load=method(b,"a",false,void.class);}load.invoke(world);
        Field mission=fieldByTypeOrdinal(b,byte.class,true,15);int loaded=(mission.getByte(null)&255)+1;
        if(loaded!=expected)throw new IllegalStateException("expected mission "+expected+" loaded "+loaded);
        byte[] table=(byte[])fieldByTypeOrdinal(b,byte[].class,true,0).get(null);
        int kind=table[(loaded-1)*4]&255,target=fieldByTypeOrdinal(b,int.class,true,13).getInt(null);
        satisfy(b,kind,target);
        if(!((Boolean)completionMethod(b).invoke(null)).booleanValue())throw new IllegalStateException("mission objective not complete");
        method(b,"m",true,void.class).invoke(null);
        int after=(mission.getByte(null)&255)+1;
        System.out.println("mission="+loaded+",target="+target+",after="+after+",save="+sha(saveBuffer(k)));
    }
}
