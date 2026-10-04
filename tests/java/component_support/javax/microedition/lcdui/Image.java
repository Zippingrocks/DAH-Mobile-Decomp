package javax.microedition.lcdui;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * TEST DOUBLE ONLY. Not a Java ME image implementation or a Windows port.
 * Records calls and supplies scripted results. Never shipped in a game artifact.
 */
public final class Image {
    public final String path;
    public static final List<String> calls = new ArrayList<String>();
    private static int nullsRemaining;
    private static int failure;

    private Image(String path) { this.path = path; }

    public static void reset(int nulls, int failMode) {
        calls.clear();
        nullsRemaining = nulls;
        failure = failMode;
    }

    public static Image createImage(String path) throws IOException {
        calls.add(path);
        if (nullsRemaining > 0) { --nullsRemaining; return null; }
        if (failure == 1) { throw new IOException("authored test failure"); }
        if (failure == 2) { throw new IllegalArgumentException("authored test failure"); }
        if (failure == 3) { throw new AssertionError("authored test error"); }
        return new Image(path);
    }
}
