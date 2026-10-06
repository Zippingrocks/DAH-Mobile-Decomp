package javax.microedition.rms;
public interface RecordComparator {
    int EQUIVALENT=0, PRECEDES=-1, FOLLOWS=1;
    int compare(byte[] left, byte[] right);
}
