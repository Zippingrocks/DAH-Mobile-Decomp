package javax.microedition.media;
import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.Sequencer;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;
public final class Manager {
    private Manager() {}
    public static Player createPlayer(InputStream stream, String type) throws IOException, MediaException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        for (int n; (n = stream.read(buffer)) != -1;) out.write(buffer, 0, n);
        return new DesktopPlayer(out.toByteArray(), type);
    }
    private static String sha256(byte[] data) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(data);
        StringBuilder out = new StringBuilder();
        for (byte value : digest) out.append(String.format("%02x", value & 255));
        return out.toString();
    }
    private static final class DesktopPlayer implements Player {
        private final byte[] data;
        private final String type;
        private int state = 100;
        private int loops = 1;
        private long time;
        private PlayerListener listener;
        private Sequencer sequencer;
        private Clip clip;
        DesktopPlayer(byte[] data, String type) { this.data=data; this.type=type; }
        public void addPlayerListener(PlayerListener listener) { this.listener=listener; }
        public void realize() { state=200; }
        public void prefetch() { state=300; }
        public int getState() { return state; }
        public void setLoopCount(int loops) { this.loops=loops; }
        private boolean isMidi() { return type != null && type.toLowerCase().contains("midi"); }
        private boolean isAmr() { return type != null && type.toLowerCase().contains("amr"); }
        private void startMidi() {
            try {
                sequencer=MidiSystem.getSequencer(false);
                sequencer.open();
                sequencer.setSequence(new ByteArrayInputStream(data));
                sequencer.setLoopCount(loops < 0 ? Sequencer.LOOP_CONTINUOUSLY : Math.max(0, loops-1));
                sequencer.start();
            } catch (Exception ignored) { sequencer=null; }
        }
        private void startConvertedAmr() {
            AudioInputStream audio = null;
            try {
                String resource="/META-INF/dah-audio/"+sha256(data)+".wav";
                InputStream in=Manager.class.getResourceAsStream(resource);
                if (in == null) return;
                audio=AudioSystem.getAudioInputStream(new BufferedInputStream(in));
                clip=AudioSystem.getClip();
                clip.open(audio);
                if (time > 0) clip.setMicrosecondPosition(Math.min(time, clip.getMicrosecondLength()));
                if (loops < 0) clip.loop(Clip.LOOP_CONTINUOUSLY);
                else if (loops > 1) clip.loop(loops-1);
                else clip.start();
            } catch (Exception ignored) {
                if (clip != null) { clip.close(); clip=null; }
            } finally {
                if (audio != null) try { audio.close(); } catch (IOException ignored) {}
            }
        }
        public void start() throws MediaException {
            state=400;
            if (isMidi()) startMidi();
            else if (isAmr()) startConvertedAmr();
        }
        public void stop() {
            if (sequencer != null) { sequencer.stop(); sequencer.close(); sequencer=null; }
            if (clip != null) { clip.stop(); clip.close(); clip=null; }
            state=300;
        }
        public long setMediaTime(long time) {
            this.time=time;
            if (sequencer != null) sequencer.setMicrosecondPosition(time);
            if (clip != null) clip.setMicrosecondPosition(Math.min(time, clip.getMicrosecondLength()));
            return time;
        }
    }
}
