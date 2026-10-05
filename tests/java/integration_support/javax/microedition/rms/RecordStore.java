package javax.microedition.rms;
import java.util.*;
/** Deterministic in-memory RMS adapter for original-vs-rebuilt integration tests.
 * It models the record-store operations used by this game only; it is not a production persistence backend.
 */
public class RecordStore {
 private static final Map<String,List<byte[]>> STORES=new HashMap<String,List<byte[]>>();
 public static final List<String> events=new ArrayList<String>();
 private final String name;
 private boolean closed;
 private RecordStore(String name){this.name=name;}
 public static void reset(){STORES.clear();events.clear();}
 public static RecordStore openRecordStore(String n,boolean create)throws RecordStoreException{
   events.add("open:"+n+":"+create);
   if(!STORES.containsKey(n)){if(!create)throw new RecordStoreException("missing");STORES.put(n,new ArrayList<byte[]>());}
   return new RecordStore(n);
 }
 public static void deleteRecordStore(String n)throws RecordStoreException{
   events.add("delete:"+n);if(STORES.remove(n)==null)throw new RecordStoreException("missing");
 }
 private List<byte[]> list()throws RecordStoreException{if(closed)throw new RecordStoreException("closed");List<byte[]> x=STORES.get(name);if(x==null)throw new RecordStoreException("deleted");return x;}
 public int getNumRecords(){List<byte[]> x=STORES.get(name);return x==null?0:x.size();}
 public byte[] getRecord(int id)throws RecordStoreException{List<byte[]>x=list();if(id<1||id>x.size())throw new RecordStoreException("bad id");byte[]v=x.get(id-1);return v==null?null:v.clone();}
 public int addRecord(byte[] d,int o,int l)throws RecordStoreException{List<byte[]>x=list();byte[]v=new byte[l];System.arraycopy(d,o,v,0,l);x.add(v);events.add("add:"+name+":"+l);return x.size();}
 public void setRecord(int id,byte[] d,int o,int l)throws RecordStoreException{List<byte[]>x=list();if(id<1||id>x.size())throw new RecordStoreException("bad id");byte[]v=new byte[l];System.arraycopy(d,o,v,0,l);x.set(id-1,v);events.add("set:"+name+":"+id+":"+l);}
 public void closeRecordStore()throws RecordStoreException{if(closed)throw new RecordStoreException("closed");closed=true;events.add("close:"+name);}
 public RecordEnumeration enumerateRecords(final RecordFilter f,final RecordComparator c,boolean keepUpdated)throws RecordStoreException{
   final List<byte[]> src=list();final ArrayList<Integer> ids=new ArrayList<Integer>();for(int i=0;i<src.size();i++)if(f==null||f.matches(src.get(i)))ids.add(i+1);
   if(c!=null)Collections.sort(ids,new Comparator<Integer>(){public int compare(Integer a,Integer b){return c.compare(src.get(a-1),src.get(b-1));}});
   events.add("enum:"+name+":"+ids.size()+":"+keepUpdated);
   return new RecordEnumeration(){int p;boolean dead;public boolean hasNextElement(){return !dead&&p<ids.size();}public byte[] nextRecord()throws RecordStoreException{return getRecord(nextRecordId());}public int nextRecordId()throws RecordStoreException{if(!hasNextElement())throw new RecordStoreException("end");return ids.get(p++);}public void destroy(){dead=true;}};
 }
}
