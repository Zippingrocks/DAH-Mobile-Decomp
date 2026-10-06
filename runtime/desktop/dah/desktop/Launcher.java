package dah.desktop;
public final class Launcher {
    public static void main(String[] args) throws Exception {
        Class<?> type = Class.forName("GameMidlet");
        Object midlet = type.getDeclaredConstructor().newInstance();
        java.lang.reflect.Method start = type.getDeclaredMethod("startApp");
        start.setAccessible(true);
        start.invoke(midlet);
    }
}
