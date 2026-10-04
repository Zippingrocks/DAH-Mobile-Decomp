/** TEST REMOVAL SINK ONLY; not the original entity collection. */
public final class n {
    public static StringBuilder events = new StringBuilder();
    public static int failure;
    public void b(o entity) {
        events.append("remove:"+entity.getClass().getName()+":"+entity.q+";");
        if(failure != 0) throw new IllegalStateException("scripted removal");
    }
}
