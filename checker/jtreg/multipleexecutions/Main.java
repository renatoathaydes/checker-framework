/*
 * @test
 * @summary Ensure that the Java Compiler API can be used multiple times
 *   to execute the Checker Framework.
 *
 * @compile -source 7 -target 7 Main.java
 * @run main Main
 */
/*
 * Test based on message by Daniil Ovchinnikov:
 * https://groups.google.com/d/msg/checker-framework-dev/FvWmCxB8OpE/Cgp1DsPwnWwJ
 */
import java.util.Arrays;

import java.io.File;

import javax.tools.JavaCompiler;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

import org.checkerframework.checker.regex.RegexChecker;

public class Main {

    public static void main(String[] args) {
        final JavaCompiler javac = ToolProvider.getSystemJavaCompiler();
        final StandardJavaFileManager fileManager = javac.getStandardFileManager(null, null, null);
        if (!doStuff(javac, fileManager)) {
            System.exit(1);
        }
        if (!doStuff(javac, fileManager)) {
            System.exit(1);
        }
        if (!doStuff(javac, fileManager)) {
            System.exit(1);
        }
    }

    public static boolean doStuff(JavaCompiler javac, StandardJavaFileManager fileManager) {
        File testfile = new File(System.getProperty("test.src", "."), "Test.java");

        JavaCompiler.CompilationTask task = javac.getTask(
                null,
                null,
                null,
                Arrays.asList(
                        "-classpath",
                        "../../dist/javac.jar:../../dist/checker.jar",
                        "-proc:only",
                        "-AprintErrorStack",
                        "-AprintAllQualifiers"
                ),
                null,
                fileManager.getJavaFileObjects(testfile)
        );
        task.setProcessors(Arrays.asList(new RegexChecker()));
        return task.call();
    }
}
