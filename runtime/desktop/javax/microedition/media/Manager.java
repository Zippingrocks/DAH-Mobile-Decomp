package javax.microedition.media;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.Sequencer;
public final class Manager {
    private Manager() {}
    public static Player createPlayer(InputStream stream, String type) throws IOException, MediaException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        for (int n; (n = stream.read(buffer)) != -1;) out.write(buffer, 0, n);
        return new DesktopPlayer(out.toByteArray(), type);
    }
    private static final class DesktopPlayer implements Player {
        private final byte[] data;
        private final String type;
        private int state = 100;
        private int loops = 1;
        private long time;
        private PlayerListener listener;
        private Sequencer sequencer;
        DesktopPlayer(byte[] data, String type) { this.data=data; this.type=type; }
        public void addPlayerListener(PlayerListener listener) { this.listener=listener; }
        public void realize() { state=200; }
        public void prefetch() { state=300; }
        public int getState() { return state; }
        public void setLoopCount(int loops) { this.loops=loops; }
        public void start() throws MediaException {
            state=400;
            if (type != null && type.toLowerCase().contains("midi")) {
                try {
                    sequencer=MidiSystem.getSequencer(false);
                    sequencer.open();
                    sequencer.setSequence(new ByteArrayInputStream(data));
                    sequencer.setLoopCount(loops < 0 ? Sequencer.LOOP_CONTINUOUSLY : Math.max(0, loops-1));
                    sequencer.start();
                } catch (Exception ignored) { sequencer=null; }
            }
        }
        public void stop() {
            if (sequencer != null) { sequencer.stop(); sequencer.close(); sequencer=null; }
            state=300;
        }
        public long setMediaTime(long time) {
            this.time=time;
            if (sequencer != null) sequencer.setMicrosecondPosition(time);
            return time;
        }
    }
}
