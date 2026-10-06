package javax.microedition.rms;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
public final class RecordStore {
    private final String name;
    private final Path path;
    private final List<byte[]> records;
    private boolean closed;
    private RecordStore(String name, Path path, List<byte[]> records) { this.name=name; this.path=path; this.records=records; }
    private static Path root() { return Paths.get(System.getProperty("dah.rms.dir", System.getProperty("user.home")+File.separator+".dah-mobile")); }
    private static Path path(String name) { return root().resolve(name.replaceAll("[^A-Za-z0-9._-]","_")+".rms"); }
    public static RecordStore openRecordStore(String name, boolean create) throws RecordStoreException {
        try {
            Files.createDirectories(root());
            Path path=path(name);
            if (!Files.exists(path)) {
                if (!create) throw new RecordStoreException("missing "+name);
                return new RecordStore(name,path,new ArrayList<byte[]>());
            }
            DataInputStream in=new DataInputStream(Files.newInputStream(path));
            try {
                int count=in.readInt();
                ArrayList<byte[]> list=new ArrayList<byte[]>(count);
                for (int i=0;i<count;i++) {
                    int len=in.readInt();
                    byte[] data=new byte[len];
                    in.readFully(data);
                    list.add(data);
                }
                return new RecordStore(name,path,list);
            } finally { in.close(); }
        } catch (IOException e) { throw new RecordStoreException("open "+name,e); }
    }
    public static void deleteRecordStore(String name) throws RecordStoreException {
        try { if (!Files.deleteIfExists(path(name))) throw new RecordStoreException("missing "+name); }
        catch (IOException e) { throw new RecordStoreException("delete "+name,e); }
    }
    private void check() throws RecordStoreException { if (closed) throw new RecordStoreException("closed"); }
    private void flush() throws RecordStoreException {
        try {
            Files.createDirectories(path.getParent());
            DataOutputStream out=new DataOutputStream(Files.newOutputStream(path, StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING));
            try {
                out.writeInt(records.size());
                for (byte[] data:records) { out.writeInt(data.length); out.write(data); }
            } finally { out.close(); }
        } catch (IOException e) { throw new RecordStoreException("write "+name,e); }
    }
    public int getNumRecords() { return records.size(); }
    public byte[] getRecord(int id) throws RecordStoreException { check(); if(id<1||id>records.size())throw new RecordStoreException("bad id"); return records.get(id-1).clone(); }
    public int addRecord(byte[] data,int offset,int length) throws RecordStoreException { check(); records.add(Arrays.copyOfRange(data,offset,offset+length)); flush(); return records.size(); }
    public void setRecord(int id,byte[] data,int offset,int length) throws RecordStoreException { check(); if(id<1||id>records.size())throw new RecordStoreException("bad id"); records.set(id-1,Arrays.copyOfRange(data,offset,offset+length)); flush(); }
    public void closeRecordStore() throws RecordStoreException { check(); flush(); closed=true; }
    public RecordEnumeration enumerateRecords(final RecordFilter filter, final RecordComparator comparator, boolean keepUpdated) throws RecordStoreException {
        check();
        final ArrayList<Integer> ids=new ArrayList<Integer>();
        for(int i=0;i<records.size();i++) if(filter==null||filter.matches(records.get(i))) ids.add(i+1);
        if(comparator!=null) Collections.sort(ids,new Comparator<Integer>(){public int compare(Integer a,Integer b){return comparator.compare(records.get(a-1),records.get(b-1));}});
        return new RecordEnumeration() {
            int index;
            boolean dead;
            public boolean hasNextElement(){return !dead&&index<ids.size();}
            public int nextRecordId() throws RecordStoreException { if(!hasNextElement())throw new RecordStoreException("end"); return ids.get(index++); }
            public byte[] nextRecord() throws RecordStoreException { return getRecord(nextRecordId()); }
            public void destroy(){dead=true;}
        };
    }
}
