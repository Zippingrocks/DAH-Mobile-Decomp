package javax.microedition.rms;
public class RecordStore {
 public static RecordStore openRecordStore(String n,boolean create)throws RecordStoreException{return new RecordStore();}
 public static void deleteRecordStore(String n)throws RecordStoreException{}
 public int getNumRecords(){return 0;}public byte[] getRecord(int id)throws RecordStoreException{return new byte[0];}
 public int addRecord(byte[] d,int o,int l)throws RecordStoreException{return 1;}public void setRecord(int id,byte[] d,int o,int l)throws RecordStoreException{}
 public void closeRecordStore()throws RecordStoreException{}
 public RecordEnumeration enumerateRecords(RecordFilter f,RecordComparator c,boolean k){return new RecordEnumeration(){public boolean hasNextElement(){return false;}public byte[] nextRecord(){return new byte[0];}public int nextRecordId(){return 1;}public void destroy(){}};}
}
