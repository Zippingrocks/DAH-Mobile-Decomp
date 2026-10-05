package javax.microedition.midlet;
public abstract class MIDlet {
 public static StringBuilder events=new StringBuilder();public static int failNew,failNotify;
 protected MIDlet(){events.append("midlet-new;");if(failNew!=0)throw new IllegalArgumentException("scripted midlet constructor");}
 public final void notifyPaused(){events.append("notify-paused;");if(failNotify!=0)throw new IllegalArgumentException("scripted notify");}
 public final void notifyDestroyed(){events.append("notify-destroyed;");if(failNotify!=0)throw new IllegalArgumentException("scripted notify");}
 protected abstract void startApp() throws MIDletStateChangeException;protected abstract void pauseApp();protected abstract void destroyApp(boolean unconditional) throws MIDletStateChangeException;
}
