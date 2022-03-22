package app;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.time.Duration;
import java.util.HashMap;
import java.util.concurrent.ExecutionException;

import com.google.common.net.InetAddresses;
import com.google.common.net.InternetDomainName;

import Server.SimpleTask;
import gnu.getopt.Getopt;
import gnu.getopt.LongOpt;
import net.spy.memcached.MemcachedClient;

public class Main {

	private static Boolean isEmu = false;
	private static String task;
	private static int port;
	private static String ipportPers;
	private static String ipportAuth;
	private static String ipportImage;
	private static String jedisHost = null;
	
	private static Duration persTime = Duration.ofMillis(60);
	private static Duration authTime = Duration.ofMillis(40);
	private static Duration imageTime = Duration.ofMillis(50);
	private static Duration webuiTime = Duration.ofMillis(100);

	public static void main(String[] args) {
		System.setProperty("net.spy.log.LoggerImpl", "net.spy.memcached.compat.log.SLF4JLogger");
		Main.getCliOptions(args);
		SimpleTask[] Sys = {};
		switch(Main.task) {
		case "persistence":
			Sys = Main.genPersistence();
			break;
		case "webui":
			Sys = Main.genWebui();
			break;
		case "image":
			Sys = Main.genImage();
			break;
		case "auth":
			Sys = Main.genAuth();
			break;
		}
		try {
			Main.resetState(Sys[0]);
		} catch (InterruptedException | ExecutionException e) {
			e.printStackTrace();
		}
		Sys[0].start();
	}

	public static void resetState(SimpleTask task) throws InterruptedException, ExecutionException {
		MemcachedClient memcachedClient=null;
		try {
			memcachedClient = new MemcachedClient(new InetSocketAddress(Main.jedisHost, 11211));
		} catch (IOException e) {
			e.printStackTrace();
		}
		memcachedClient.set(task.getName()+"_sw", 3600,"1").get();
		memcachedClient.set(task.getName()+"_hw", 3600,"1").get();
		String[] entries = task.getEntries().keySet().toArray(new String[0]);
		for (String e : entries) {
			memcachedClient.set(e + "_bl",Integer.MAX_VALUE, "0").get();
			memcachedClient.set(e + "_ex",Integer.MAX_VALUE,"0").get();
		}
		memcachedClient.shutdown();
	}
	
	public static SimpleTask[] genPersistence() {
		HashMap<String, Class> t1Entries = new HashMap<String, Class>();
		HashMap<String, Long> t1Entries_stimes = new HashMap<String, Long>();
		
		t1Entries.put("categories", LeafHTTPHandler.class);
		t1Entries_stimes.put("categories", persTime.toMillis());
		
		final SimpleTask persistence = new SimpleTask("localhost", port, t1Entries, t1Entries_stimes, 1, Main.isEmu, "persistence",
				Main.jedisHost,100l);
		persistence.setHwCore(1f);
		
		return new SimpleTask[] { persistence };
	}
	
	public static SimpleTask[] genAuth() {
		HashMap<String, Class> t1Entries = new HashMap<String, Class>();
		HashMap<String, Long> t1Entries_stimes = new HashMap<String, Long>();
		
		t1Entries.put("isloggedin", LeafHTTPHandler.class);
		t1Entries_stimes.put("isloggedin", authTime.toMillis());
		
		final SimpleTask auth = new SimpleTask("localhost", port, t1Entries, t1Entries_stimes, 1, Main.isEmu, "auth",
				Main.jedisHost,100l);
		auth.setHwCore(1f);
		
		return new SimpleTask[] { auth };
	}
	
	public static SimpleTask[] genImage() {
		HashMap<String, Class> t1Entries = new HashMap<String, Class>();
		HashMap<String, Long> t1Entries_stimes = new HashMap<String, Long>();
		
		t1Entries.put("getWebImages", LeafHTTPHandler.class);
		t1Entries_stimes.put("getWebImages", imageTime.toMillis());
		
		final SimpleTask image = new SimpleTask("localhost", port, t1Entries, t1Entries_stimes, 1, Main.isEmu, "image",
				Main.jedisHost,100l);
		image.setHwCore(1f);
		
		return new SimpleTask[] { image };
	}
	
	public static SimpleTask[] genWebui() {
		HashMap<String, Class> t1Entries = new HashMap<String, Class>();
		HashMap<String, Long> t1Entries_stimes = new HashMap<String, Long>();
		
		t1Entries.put("index", SyncCallsHTTPHandler.class);
		t1Entries_stimes.put("index", webuiTime.toMillis());
		
		SyncCallsHTTPHandler.addCalls("webui", "index", 
				new String[][] {{Main.ipportPers, "categories"}, 
					{Main.ipportAuth, "isloggedin"}, 
					{Main.ipportImage, "getWebImages"}});
		
		final SimpleTask image = new SimpleTask("localhost", port, t1Entries, t1Entries_stimes, 1, Main.isEmu, "webui",
				Main.jedisHost,100l);
		image.setHwCore(1f);
		
		return new SimpleTask[] { image };
	}
/*
	public static SimpleTask[] genSystem() {
		// instatiate tier2 class
		HashMap<String, Class> t1Entries = new HashMap<String, Class>();
		HashMap<String, Long> t1Entries_stimes = new HashMap<String, Long>();
		Tier1HTTPHandler.setTier2Host(Main.tier2Host);
		t1Entries.put("e1", Tier1HTTPHandler.class);
		t1Entries_stimes.put("e1", 100l);
		final SimpleTask t1 = new SimpleTask("localhost", 3000, t1Entries, t1Entries_stimes, 1, Main.isEmu, "t1",
				Main.jedisHost,100l);
		t1.setHwCore(1f);
		return new SimpleTask[] { t1 };
	}*/
	
	public static boolean validate(final String hostname) {
        return InetAddresses.isUriInetAddress(hostname) || 
        		InternetDomainName.isValid(hostname);
    }

	public static void getCliOptions(String[] args) {

		int c;
		LongOpt[] longopts = new LongOpt[7];
		longopts[0] = new LongOpt("cpuEmu", LongOpt.REQUIRED_ARGUMENT, null, 0);
		longopts[1] = new LongOpt("jedisHost", LongOpt.REQUIRED_ARGUMENT, null, 1);
		longopts[2] = new LongOpt("task", LongOpt.REQUIRED_ARGUMENT, null, 2);
		longopts[3] = new LongOpt("port", LongOpt.REQUIRED_ARGUMENT, null, 3);
		longopts[4] = new LongOpt("persistence", LongOpt.REQUIRED_ARGUMENT, null, 4);
		longopts[5] = new LongOpt("auth", LongOpt.REQUIRED_ARGUMENT, null, 5);
		longopts[6] = new LongOpt("image", LongOpt.REQUIRED_ARGUMENT, null, 6);
		

		Getopt g = new Getopt("ddctrl", args, "", longopts);
		g.setOpterr(true);
		while ((c = g.getopt()) != -1) {
			switch (c) {
			case 0:
				try {
					Main.isEmu = Integer.valueOf(g.getOptarg()) > 0 ? true : false;
				} catch (NumberFormatException e) {
					System.err.println(String.format("%s is not valid, it must be 0 or 1.", g.getOptarg()));
				}
				break;
			case 1:
				try {
					if (!Main.validate(g.getOptarg())) {
						throw new Exception(String.format("%s is not a valid jedis HOST", g.getOptarg()));
					}
					Main.jedisHost = String.valueOf(g.getOptarg());
				} catch (Exception e) {
					e.printStackTrace();
				}
				break;
			case 2:
				try {
					Main.task = g.getOptarg();
					if(!(Main.task.equals("persistence") || Main.task.equals("webui")
							|| Main.task.equals("image") || Main.task.equals("auth"))){
						throw new Exception(String.format("%s is not a valid task (persistence, webui, image, auth)", g.getOptarg()));
					}
				} catch (Exception e) {
					e.printStackTrace();
				}
				break;
			case 3:
				try {
					Main.port = Integer.valueOf(g.getOptarg());
				} catch (NumberFormatException e) {
					System.err.println(String.format("%s is not a valid port.", g.getOptarg()));
				}
				break;
			case 4:
				/*try {
					if (!Main.validate(g.getOptarg())) {
						throw new Exception(String.format("%s is not a valid persistence address", g.getOptarg()));
					}*/
					Main.ipportPers = String.valueOf(g.getOptarg());
				/*} catch (Exception e) {
					e.printStackTrace();
				}*/
				break;
			case 5:
				/*try {
					if (!Main.validate(g.getOptarg())) {
						throw new Exception(String.format("%s is not a valid auth address", g.getOptarg()));
					}*/
					Main.ipportAuth = String.valueOf(g.getOptarg());
				/*} catch (Exception e) {
					e.printStackTrace();
				}*/
				break;
			case 6:
				/*try {
					if (!Main.validate(g.getOptarg())) {
						throw new Exception(String.format("%s is not a valid image address", g.getOptarg()));
					}*/
					Main.ipportImage = String.valueOf(g.getOptarg());
				/*} catch (Exception e) {
					e.printStackTrace();
				}*/
				break;
			default:
				break;
			}
		}
	}

}
