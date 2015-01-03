package uk.ac.ljmu.automark;

import java.util.Scanner;

public class JOptionPane
{
  static Scanner console = new Scanner(System.in);

	public static final int WARNING_MESSAGE = 0;
	public static final int ERROR_MESSAGE = 1;
	public static final int PLAIN_MESSAGE = 2;
	public static final int INFORMATION_MESSAGE = 3;

	public static void showMessageDialog(Object parent, String text, String title, int type) {
		System.out.println(title + " : " + text);
	}

	public static void showMessageDialog(Object parent, String text, int type) {
		System.out.println(text);
	}

	public static void showMessageDialog(Object parent, String text) {
		System.out.println(text);
	}

	public static String showInputDialog(String text) {
		System.out.println(text);
		return console.nextLine();
	}
}

