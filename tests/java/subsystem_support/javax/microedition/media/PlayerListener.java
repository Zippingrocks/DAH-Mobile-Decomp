package javax.microedition.media;
/** Interface subset used by the scoped probe. */
public interface PlayerListener {
    void playerUpdate(Player player, String event, Object data);
}
