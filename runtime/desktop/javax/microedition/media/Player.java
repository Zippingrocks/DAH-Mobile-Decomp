package javax.microedition.media;
public interface Player {
    void addPlayerListener(PlayerListener listener);
    void realize() throws MediaException;
    void prefetch() throws MediaException;
    int getState();
    void setLoopCount(int loops);
    void start() throws MediaException;
    void stop() throws MediaException;
    long setMediaTime(long time) throws MediaException;
}
