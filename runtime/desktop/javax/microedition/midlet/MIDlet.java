package javax.microedition.midlet;
public abstract class MIDlet {
    protected MIDlet() {}
    public final void notifyPaused() {}
    public final void notifyDestroyed() {}
    protected abstract void startApp() throws MIDletStateChangeException;
    protected abstract void pauseApp();
    protected abstract void destroyApp(boolean unconditional) throws MIDletStateChangeException;
}
