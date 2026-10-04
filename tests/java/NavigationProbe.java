import java.io.*;
import java.lang.reflect.*;
import java.util.*;
/** Independent differential inputs for the recovered navigation component.
 * World/actor objects are test records, not recovered AI or a running world.
 */
public final class NavigationProbe {
    static Class<?> Q,E,B,K;
    static Field x,y,links,choices,header,second,width,height,rng,primary,fallback,bx,by;
    static final Class<?>[] II={int.class,int.class},IB={int.class,byte.class};
    static void emit(Object v)throws Exception{SubsystemProbe.emit(v);}
    static Object call(String name,Class<?>[] types,Object...args)throws Exception{
        Object value=SubsystemProbe.invoke(SubsystemProbe.method(Q,name,byte.class,types),null,args);
        emit(choices.get(null));return value;
    }
    static void state()throws Exception{emit(x.get(null));emit(y.get(null));emit(links.get(null));emit(choices.get(null));emit(header.get(null));emit(second.get(null));}
    static void setup(int count,Random r,boolean acyclic)throws Exception{
        short[] xs=new short[count],ys=new short[count];int[] edges=new int[count];
        for(int i=0;i<count;++i){
            xs[i]=(short)(r.nextInt(900)-400);ys[i]=(short)(r.nextInt(900)-400);
            int value=0;
            for(int j=0;j<4;++j){
                int next=acyclic?(i+1<count&&r.nextBoolean()?i+1+r.nextInt(count-i-1):0):r.nextInt(256);
                value=(value<<8)|next;
            }
            edges[i]=value;
        }
        x.set(null,xs);y.set(null,ys);links.set(null,edges);
    }
    public static final class ScriptedRandom extends Random {
        public int result,calls;
        ScriptedRandom(int result){this.result=result;}
        public int nextInt(){++calls;return result;}
    }
    static void loading()throws Exception{
        SubsystemProbe.begin();state();Random r=new Random(0x4e41564cL);
        byte[] payload=new byte[105];r.nextBytes(payload);
        for(int count:new int[]{-1,0,1,2,4,16,128})for(int cut=0;cut<=payload.length;++cut)for(boolean phase:new boolean[]{false,true}){
            header.setByte(null,(byte)0xa5);second.setBoolean(null,phase);
            DataInputStream stream=new DataInputStream(new ByteArrayInputStream(Arrays.copyOf(payload,cut)));
            SubsystemProbe.construct(Q,new Class<?>[]{int.class,DataInputStream.class},count,stream);
            state();emit(stream.available());
        }
        SubsystemProbe.construct(Q,new Class<?>[]{int.class,DataInputStream.class},2,null);state();
        SubsystemProbe.invoke(SubsystemProbe.method(Q,"a",void.class),null);state();
        SubsystemProbe.finish("navigation-loading-and-partial-state");
    }
    static void selectors()throws Exception{
        SubsystemProbe.begin();Random r=new Random(0x4e415653L);int[] edge=new int[2];
        x.set(null,new short[]{0,0});y.set(null,new short[]{0,0});links.set(null,edge);
        for(int sample=0;sample<5000;++sample){
            edge[1]=sample<256?sample*0x01010101:r.nextInt();
            for(String name:new String[]{"c","d","e","f"})call(name,new Class<?>[]{int.class},1);
            for(byte direction:new byte[]{-128,-1,0,1,2,3,4,127}){
                call("b",IB,1,direction);
                ScriptedRandom sr=new ScriptedRandom(sample%3==0?Integer.MIN_VALUE:sample%3==1?Integer.MAX_VALUE:r.nextInt());rng.set(null,sr);
                call("c",IB,1,direction);emit(sr.calls);
            }
        }
        // No candidate: no RNG invocation, and existing scratch bytes remain.
        edge[1]=0;rng.set(null,null);call("c",IB,1,(byte)0);
        for(int index:new int[]{-1,0,1,2,Integer.MIN_VALUE,Integer.MAX_VALUE})for(String name:new String[]{"c","d","e","f"})call(name,new Class<?>[]{int.class},index);
        SubsystemProbe.finish("navigation-packed-links-and-random-selection");
    }
    static void queries()throws Exception{
        SubsystemProbe.begin();Random r=new Random(0x4e415651L);
        for(int trial=0;trial<500;++trial){
            int n=trial%25==0?128:r.nextInt(35)+1;setup(n,r,true);
            bx.setShort(null,(short)(r.nextInt(1000)-500));by.setShort(null,(short)(r.nextInt(1000)-500));
            width.setInt(null,new int[]{0,1,176,-1,Integer.MAX_VALUE}[r.nextInt(5)]);height.setInt(null,208);
            j actor=new j();f other=new f();((o)actor).k=r.nextInt(1000)-500;actor.l=r.nextInt(1000)-500;
            ((o)other).k=r.nextInt(1000)-500;other.l=r.nextInt(1000)-500;actor.k=(byte)(n>1?1:0);
            primary.set(null,trial%4==0?null:actor);fallback.set(null,trial%5==0?null:other);
            for(int rep=0;rep<12;++rep){
                int node=r.nextInt(n+2)-1;
                call("a",new Class<?>[]{int.class,int.class,boolean.class},r.nextInt(),r.nextInt(),rep%2==0);
                call("a",IB,node,(byte)(rep%4));
                call("a",new Class<?>[]{int.class},node);call("b",new Class<?>[]{int.class},node);
            }
            call("a",new Class<?>[]{j.class},actor);call("a",new Class<?>[]{j.class},(Object)null);
        }
        // Inclusive camera edges, ties and offscreen fallback.
        bx.setShort(null,(short)0);by.setShort(null,(short)0);width.setInt(null,176);height.setInt(null,208);
        x.set(null,new short[]{0,-11,-10,0,186,187,0,0});y.set(null,new short[]{0,0,0,0,0,0,-10,219});
        links.set(null,new int[]{0,2<<8,3<<8,4<<8,5<<8,0,0,0});
        for(int a:new int[]{Integer.MIN_VALUE,-11,-10,0,176,186,187,Integer.MAX_VALUE})for(int b:new int[]{-11,-10,0,218,219}){
            call("a",new Class<?>[]{int.class,int.class,boolean.class},a,b,true);call("a",new Class<?>[]{int.class,int.class,boolean.class},a,b,false);
        }
        for(int node=0;node<8;++node)call("a",IB,node,(byte)2);
        SubsystemProbe.finish("navigation-spatial-queries-and-boundaries");
    }
    public static void main(String[]args)throws Exception{
        SubsystemProbe.candidate=Boolean.parseBoolean(args[0]);
        Q=Class.forName("q");E=Class.forName("e");B=Class.forName("b");K=Class.forName("k");
        x=SubsystemProbe.field(Q,"a","x",short[].class);y=SubsystemProbe.field(Q,"b","y",short[].class);
        links=SubsystemProbe.field(Q,"a","links",int[].class);choices=SubsystemProbe.field(Q,"a","choices",byte[].class);
        header=SubsystemProbe.field(E,"a","packedHeader",byte.class);second=SubsystemProbe.field(E,"a","secondPackedValue",boolean.class);
        bx=SubsystemProbe.field(B,"b","b",short.class);by=SubsystemProbe.field(B,"c","c",short.class);
        width=SubsystemProbe.field(K,"a","width",int.class);height=SubsystemProbe.field(K,"b","height",int.class);
        rng=SubsystemProbe.field(K,"a","rng",Random.class);primary=SubsystemProbe.field(B,"a","primary",j.class);fallback=SubsystemProbe.field(B,"a","fallback",f.class);
        loading();selectors();queries();
    }
}
