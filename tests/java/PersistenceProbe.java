import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
public final class PersistenceProbe {
  static String hex(byte[] data)throws Exception{byte[]d=MessageDigest.getInstance("SHA-256").digest(data);StringBuilder b=new StringBuilder();for(byte x:d)b.append(String.format("%02x",x&255));return b.toString();}
  static Field saveArray()throws Exception{Class<?> c=Class.forName("k");for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType()==byte[].class){f.setAccessible(true);return f;}throw new IllegalStateException();}
  static Field loadedFlag()throws Exception{Class<?> c=Class.forName("k");for(Field f:c.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&Modifier.isPrivate(f.getModifiers())&&f.getType()==boolean.class){f.setAccessible(true);return f;}throw new IllegalStateException();}
  static Method privateLoad()throws Exception{Class<?> c=Class.forName("k");for(Method m:c.getDeclaredMethods())if(Modifier.isPrivate(m.getModifiers())&&Modifier.isStatic(m.getModifiers())&&m.getParameterTypes().length==0&&m.getReturnType()==void.class){m.setAccessible(true);return m;}throw new IllegalStateException();}
  public static void main(String[]args)throws Exception{
    javax.microedition.rms.RecordStore.reset();
    Field arrF=saveArray(), loaded=loadedFlag();Method load=privateLoad();
    byte[] arr=(byte[])arrF.get(null);Arrays.fill(arr,(byte)0x55);arr[0]=1;arr[17]=(byte)0xA7;arr[80]=1;arr[81]=(byte)0xFE;
    Class<?> k=Class.forName("k");Method save=k.getDeclaredMethod("h");save.setAccessible(true);save.invoke(null);
    String saved=hex(arr.clone());Arrays.fill(arr,(byte)0);loaded.setBoolean(null,false);load.invoke(null);
    byte[] restored=((byte[])arrF.get(null)).clone();
    System.out.println("saved="+saved);System.out.println("restored="+hex(restored));
    System.out.println("bytes="+(restored[0]&255)+","+(restored[17]&255)+","+(restored[80]&255)+","+(restored[81]&255));
    System.out.println("events="+hex(javax.microedition.rms.RecordStore.events.toString().getBytes(StandardCharsets.UTF_8)));
    javax.microedition.rms.RecordStore.reset();Arrays.fill((byte[])arrF.get(null),(byte)9);loaded.setBoolean(null,false);load.invoke(null);byte[] defaults=((byte[])arrF.get(null)).clone();
    System.out.println("default="+hex(defaults)+":"+(defaults[80]&255));
  }
}
