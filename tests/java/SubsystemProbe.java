import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.media.Manager;
import javax.microedition.media.Player;

/** Independently authored differential probe. Not recovered game source.
 * Separate JVM/classpaths per side; snapshots compare observations, not invented
 * expected implementations. Raster checks are under the same test adapter only.
 */
public final class SubsystemProbe {
    static boolean candidate;
    static MessageDigest digest;
    static long calls;
    static Class<?> G, L;
    static final String[] GN={"a","a","a","b","a","a","b"};
    static final String[] GC={"player","samples","formats","capacity","selected","enabled","playing"};
    static final Class<?>[] GT={Player.class,byte[][].class,byte[].class,int.class,int.class,boolean.class,boolean.class};
    static final String[] LN={"a","a","a","b","a","c","b","d","c","b","a","b","d"};
    static final String[] LC={"atlas","advances","spaceAdvance","digitBase","glyphX","atlasY","glyphWidths","glyphHeight","strings","stringOffsets","charToGlyph","glyphToChar","numberScratch"};
    static final Class<?>[] LT={Image.class,byte[].class,byte.class,byte.class,short[].class,byte.class,byte[].class,byte.class,byte[].class,short[].class,char[].class,char[].class,byte[].class};
    static Field field(Class<?> owner,String name,String alias,Class<?> type) throws Exception {
        for(Field f:owner.getDeclaredFields()) if(f.getName().equals(candidate?alias:name)&&f.getType()==type) {
            f.setAccessible(true); return f;
        }
        throw new NoSuchFieldException(owner+":"+name+":"+type);
    }
    static Field gf(int index) throws Exception { return field(G,GN[index],GC[index],GT[index]); }
    static Field lf(int index) throws Exception { return field(L,LN[index],LC[index],LT[index]); }
    static Method method(Class<?> owner,String name,Class<?> result,Class<?>... params) throws Exception {
        if(candidate&&owner==L&&result==byte.class) {
            if(name.equals("a")) name="encodedByte";
            if(name.equals("b")) name="glyphOffsetByte";
        }
        for(Method m:owner.getDeclaredMethods()) if(m.getName().equals(name)&&m.getReturnType()==result&&Arrays.equals(m.getParameterTypes(),params)) {
            m.setAccessible(true);return m;
        }
        throw new NoSuchMethodException(owner+":"+name+":"+result);
    }
    static void word(String text) { digest.update(text.getBytes(StandardCharsets.UTF_8));digest.update((byte)0); }
    static String hex(byte[] bytes) { StringBuilder s=new StringBuilder();for(byte b:bytes)s.append(String.format("%02x",b&255));return s.toString(); }
    static void emit(Object value) throws Exception {
        if(value==null){word("null");return;}
        if(value instanceof Image){word("image:"+((Image)value).path);return;}
        if(value instanceof Manager.FakePlayer){Manager.FakePlayer p=(Manager.FakePlayer)value;word("player:"+p.id+":"+p.state+":"+p.loops+":"+p.time+":"+(p.listener!=null));return;}
        if(value instanceof byte[]){byte[] b=(byte[])value;word("[B:"+b.length+":"+hex(MessageDigest.getInstance("SHA-256").digest(b)));return;}
        if(value.getClass().isArray()) {
            word(value.getClass().getName()+":"+Array.getLength(value));
            for(int i=0;i<Array.getLength(value);++i)emit(Array.get(value,i));return;
        }
        word(value.getClass().getName()+":"+String.valueOf(value));
    }
    static void begin(){try{digest=MessageDigest.getInstance("SHA-256");calls=0;}catch(Exception e){throw new AssertionError(e);}}
    static void finish(String label){System.out.println(label+"\t"+calls+"\t"+hex(digest.digest()));}
    static Object invoke(Method m,Object target,Object... args) throws Exception {
        ++calls;
        try{Object value=m.invoke(target,args);word("return");emit(value);return value;}
        catch(InvocationTargetException ex){word("throw:"+ex.getCause().getClass().getName());return null;}
    }
    static Object construct(Class<?> owner,Class<?>[] types,Object... args) throws Exception {
        ++calls;Constructor<?> c=owner.getDeclaredConstructor(types);c.setAccessible(true);
        try{Object value=c.newInstance(args);word("constructed");return value;}
        catch(InvocationTargetException ex){word("throw:"+ex.getCause().getClass().getName());return null;}
    }
    static Object audio() throws Exception { return construct(G,new Class<?>[0]); }
    static Object font(String metrics,String chars) throws Exception {
        return construct(L,new Class<?>[]{String.class,String.class,String.class},"/pics/fnt1.png",metrics,chars);
    }
    static Object acall(Object obj,String name,Class<?> result,Class<?>[] args,Object...values) throws Exception {
        Object ret=invoke(method(G,name,result,args),obj,values); audioState(obj);return ret;
    }
    static void audioState(Object obj) throws Exception {
        for(int i=0;i<GT.length;++i)emit(gf(i).get(obj));
        emit(Manager.calls.toArray(new String[0]));
        for(Manager.FakePlayer p:Manager.players)emit(p);
        emit(Manager.remaining);Manager.calls.clear();
    }
    static void fontState(Object obj) throws Exception {
        if(obj!=null){for(int i=0;i<LT.length;++i)emit(lf(i).get(obj));emit(lf(1).get(obj)==lf(6).get(obj));}
        emit(Image.calls.toArray(new String[0]));Image.calls.clear();
    }
    static final Class<?>[] NONE={}, INT={int.class}, BOOL={boolean.class}, REGISTER={int.class,String.class}, PLAY={int.class,boolean.class};
    static void audioResources() throws Exception {
        begin();Manager.reset();Object obj=audio();audioState(obj);
        for(String path:new String[]{"/Sound/theme.mid","/Sound/select.amr","/audio/all.amr","/audio/empty.mid","/missing",null}){
            acall(obj,"a",byte[].class,new Class<?>[]{String.class},path);
        }
        for(int size:new int[]{-1,0,4,2,8,8,0,3}) acall(obj,"a",void.class,INT,size);
        for(String base:new String[]{"/audio/all","/audio/wave","/audio/midi","/audio/empty","/audio/nope",null,"/Sound/select","/Sound/theme"}){
            for(int index:new int[]{-1,0,1,2,3,Integer.MAX_VALUE}) acall(obj,"a",boolean.class,REGISTER,index,base);
        }
        finish("audio-resources-and-resize");
    }
    static void audioSequences() throws Exception {
        begin();Random r=new Random(0x47323032L);
        for(int trial=0;trial<240;++trial){
            Manager.reset();Object obj=audio();acall(obj,"a",void.class,INT,4);
            acall(obj,"a",boolean.class,REGISTER,0,"/audio/all");acall(obj,"a",boolean.class,REGISTER,1,"/audio/midi");
            for(int step=0;step<55;++step){
                int index=r.nextInt(6)-1;
                Manager.faultPoint=r.nextInt(10);Manager.faultMode=r.nextInt(4)+1;Manager.remaining=(step%5==0?1:0);
                switch(r.nextInt(9)){
                    case 0:acall(obj,"a",void.class,BOOL,r.nextBoolean());break;
                    case 1:acall(obj,"b",void.class,INT,index);break;
                    case 2:acall(obj,"a",void.class,PLAY,index,r.nextBoolean());break;
                    case 3:acall(obj,"b",void.class,NONE);break;
                    case 4:acall(obj,"a",void.class,NONE);break;
                    case 5:acall(obj,"c",void.class,INT,index);break;
                    case 6:
                        String event=step%3==0?"error":step%3==1?new String("error"):null;
                        acall(obj,"playerUpdate",void.class,new Class<?>[]{Player.class,String.class,Object.class},null,event,null);break;
                    case 7:acall(obj,"a",boolean.class,REGISTER,index,r.nextBoolean()?"/audio/wave":"/audio/nope");break;
                    default:Manager.prefetchedState=new int[]{0,100,200,300,400}[r.nextInt(5)];acall(obj,"a",void.class,INT,r.nextInt(7)-1);break;
                }
            }
        }
        finish("audio-scripted-lifecycle");
        begin();
        for(int point=1;point<=9;++point)for(int mode=1;mode<=5;++mode)for(int state:new int[]{0,100,200,300,400}){
            Manager.reset();Object obj=audio();acall(obj,"a",void.class,INT,1);acall(obj,"a",boolean.class,REGISTER,0,"/audio/all");
            Manager.prefetchedState=state;Manager.faultPoint=point;Manager.faultMode=mode;Manager.remaining=1;
            acall(obj,"a",void.class,PLAY,0,true);acall(obj,"b",void.class,NONE);acall(obj,"a",void.class,NONE);
        }
        Manager.reset();Object obj=audio();acall(obj,"a",void.class,INT,1);acall(obj,"a",boolean.class,REGISTER,0,"/audio/all");
        Manager.returnNull=true;acall(obj,"b",void.class,INT,0);acall(obj,"a",void.class,PLAY,0,false);
        finish("audio-fault-matrix");
    }
    static void fontLoading() throws Exception {
        begin();
        for(int cut=0;cut<=356;++cut){Image.reset(0,0);Object obj=font("/font-cuts/"+cut,"/fnt1.def");fontState(obj);}
        for(String metric:new String[]{"/fnt1.font","/font-alias","/font-negative","/missing"})for(String chars:new String[]{"/fnt1.def","/chars-empty","/chars-255","/chars-long","/missing"}){
            Image.reset(0,0);Object obj=font(metric,chars);fontState(obj);
        }
        for(int fail=0;fail<4;++fail){Image.reset(1,fail);Object obj=font("/fnt1.font","/fnt1.def");fontState(obj);}
        finish("font-construction-and-partial-reads");
        begin();Image.reset(0,0);Object obj=font("/fnt1.font","/fnt1.def");
        Method load=method(L,"a",void.class,String.class),clear=method(L,"a",void.class);
        for(int cut=0;cut<=64;++cut){invoke(load,obj,"/text-cuts/"+cut);fontState(obj);}
        for(String path:new String[]{"/en.bin","/de.bin","/fr.bin","/it.bin","/es.bin","/common.bin","/text-negative","/missing",null}){
            invoke(load,obj,path);fontState(obj);invoke(clear,obj);fontState(obj);
        }
        finish("font-text-tables-and-failures");
    }
    static void fontLogic() throws Exception {
        begin();Image.reset(0,0);Object obj=font("/fnt1.font","/fnt1.def");
        Method number=method(L,"a",byte[].class,int.class);Random r=new Random(0x4c323032L);
        Object shared=null;
        for(byte base:new byte[]{-128,-1,0,26,127}){
            lf(3).setByte(obj,base);
            for(int value=-256;value<1400;++value){Object ret=invoke(number,obj,value);emit(shared==null||shared==ret);shared=ret;}
            for(int i=0;i<1200;++i)invoke(number,obj,r.nextInt());
        }
        finish("font-number-formatting");
        begin();obj=font("/fnt1.font","/fnt1.def");invoke(method(L,"a",void.class,String.class),obj,"/en.bin");
        Method width=method(L,"b",int.class,int.class,int.class),line=method(L,"a",int.class,int.class,int.class);
        Method encoded=method(L,"a",byte.class,int.class,int.class),relative=method(L,"b",byte.class,int.class,int.class);
        short[] offsets=(short[])lf(9).get(obj);
        for(int id=-1;id<=offsets.length;++id)for(int offset:new int[]{-1,0,1,2,8,30,99999}){
            invoke(width,obj,id,offset);invoke(encoded,obj,id,offset);invoke(relative,obj,id,offset);
            if(offset<9)invoke(line,obj,offset,id);
        }
        Method arrayWidth=method(L,"a",int.class,byte[].class),offsetWidth=method(L,"a",int.class,byte[].class,int.class);
        for(int n=0;n<5000;++n){
            byte[] text=new byte[r.nextInt(40)];r.nextBytes(text);
            invoke(arrayWidth,obj,(Object)text);invoke(offsetWidth,obj,text,r.nextInt(45)-3);
        }
        invoke(arrayWidth,obj,(Object)null);invoke(offsetWidth,obj,null,0);
        finish("font-measurement-and-token-access");
    }
    static void draw(Method method,Object obj,Object...args) throws Exception {
        Graphics gr=(Graphics)args[0];invoke(method,obj,args);if(gr!=null)emit(gr.snapshot());
    }
    static void fontRendering() throws Exception {
        begin();Image.reset(0,0);Object obj=font("/fnt1.font","/fnt1.def");invoke(method(L,"a",void.class,String.class),obj,"/en.bin");
        Method plain=method(L,"b",void.class,Graphics.class,int.class,int.class,int.class);
        Method center=method(L,"a",void.class,Graphics.class,int.class,int.class,int.class);
        Method multi=method(L,"a",int.class,Graphics.class,int.class,int.class,int.class,int.class,int.class,boolean.class,int.class);
        Method encoded=method(L,"a",void.class,Graphics.class,int.class,int.class,byte[].class);
        int size=((short[])lf(9).get(obj)).length;
        for(int id=0;id<size;++id){
            Graphics a=new Graphics();a.setClip(3,5,160,190);draw(plain,obj,a,0,20,id);
            Graphics b=new Graphics();b.setClip(3,5,160,190);draw(center,obj,b,88,20,id);
            Graphics c=new Graphics();c.setClip(3,5,160,190);draw(multi,obj,c,88,10,4,id,0,true,13);
        }
        finish("font-real-text-raster-and-command-traces");
        begin();Random r=new Random(0x4c525354L);
        for(int n=0;n<650;++n){
            byte[] text=new byte[r.nextInt(50)+1];
            for(int i=0;i<text.length-1;++i)text[i]=(byte)new int[]{0,1,2,3,4,5,10,26,40,85,100,-1,-128}[r.nextInt(13)];
            text[text.length-1]=0;lf(8).set(obj,text);lf(9).set(obj,new short[]{0});
            int x=new int[]{-200,-1,0,175,176,177,88}[r.nextInt(7)],y=r.nextInt(220)-20;
            Graphics a=new Graphics();if(n%7==0)a.throwAtDraw=0;draw(encoded,obj,a,x,y,text);
            Graphics b=new Graphics();if(n%7==0)b.throwAtDraw=0;draw(multi,obj,b,x,y,r.nextInt(5)-1,0,0,r.nextBoolean(),12);
        }
        lf(8).set(obj,new byte[]{4,1,10,0});lf(9).set(obj,new short[]{0});
        draw(multi,obj,new Graphics(),20,20,2,0,0,false,12); // Early return without clip restoration.
        draw(encoded,obj,new Graphics(),176,0,null); // Boundary short circuit before array length.
        draw(encoded,obj,null,0,0,new byte[]{4,0});
        finish("font-layout-boundaries-and-exceptions");
    }
    public static void main(String[] args) throws Exception {
        candidate=Boolean.parseBoolean(args[0]);G=Class.forName("g");L=Class.forName("l");
        if(args[1].equals("audio")){audioResources();audioSequences();}
        else if(args[1].equals("font")){fontLoading();fontLogic();fontRendering();}
        else throw new IllegalArgumentException("probe mode");
    }
}
