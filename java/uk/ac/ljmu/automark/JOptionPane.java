package uk.ac.ljmu.automark;

import java.util.Scanner;

public class JOptionPane
{
  static Scanner console = new Scanner(System.in);

	public static final int WARNING_MESSAGE = 0;
	public static final int ERROR_MESSAGE = 1;
	public static final int PLAIN_MESSAGE = 2;
	public static final int INFORMATION_MESSAGE = 3;
	public static final int QUESTION_MESSAGE = 4;

	public static void showMessageDialog(Object parent, String message) {
		System.out.println(message);
	}

	public static void showMessageDialog(Object parent, String message, String title, int type) {
		System.out.println(title + " : " + message);
	}

	public static String showInputDialog(Object parent, String message) {
		System.out.println(message);
		return console.nextLine();
	}

	public static String showInputDialog(Object parent, String message, String initialSelection) {
		System.out.println(message);
		return console.nextLine();
	}

	public static String showInputDialog(Object parent, String message, String title, int type) {
		System.out.println(title + " : " + message);
		return console.nextLine();
	}

	public static String showInputDialog(String message) {
		System.out.println(message);
		return console.nextLine();
	}

	public static String showInputDialog(String message, int type) {
		System.out.println(message);
		return console.nextLine();
	}

	public static String showInputDialog(String message, String initialSelection) {
		System.out.println(message);
		return console.nextLine();
	}
}

