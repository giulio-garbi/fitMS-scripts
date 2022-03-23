package app;

import java.io.IOException;
import java.io.OutputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.util.HashMap;
import java.util.Map;

import com.google.common.collect.Maps;
import com.hubspot.jinjava.Jinjava;
import com.sun.net.httpserver.HttpExchange;

import Server.SimpleTask;
import Server.TierHttpHandler;
import kong.unirest.Unirest;
import monitoring.rtSample;

public class SyncCallsHTTPHandler extends TierHttpHandler {
	
	private final String taskName;
	private String entryName = "";
	public static final HashMap<String, HashMap<String, String[][]>> callsMap = new HashMap<>(); // pairs(taskip:port, endpoint)

	public static void addCalls(String task, String entry, String[][] calls) {
		callsMap.computeIfAbsent(task, x->new HashMap<>()).put(entry, calls);
	}
	
	public SyncCallsHTTPHandler(SimpleTask lqntask, HttpExchange req, long stime) {
		super(lqntask, req, stime);
		this.taskName = lqntask.getName();
	}

	public void handleResponse(HttpExchange req, String requestParamValue) throws InterruptedException, IOException {
		Map<String, String> params = this.getLqntask().queryToMap(req.getRequestURI().getQuery());
		String entryName = params.get("entry");

		Jinjava jinjava = new Jinjava();
		Map<String, Object> context = Maps.newHashMap();
		context.put("task", taskName);
		context.put("entry", entryName);

		//HttpClient client = null;
		//HttpRequest request = null;
		//client = HttpClient.newBuilder().version(Version.HTTP_1_1).build();

		String renderedTemplate = jinjava.render(this.getWebPageTpl(), context);
		
		//String[][] calls = callsMap.get(taskName).get(entryName);
		/*for(String[] call:calls) {
			request = HttpRequest.newBuilder().uri(URI.create("http://" + call[0] + "/?id="+params.get("id")
					+ "&entry="+call[1] + "&snd="+this.taskName+"-"+this.entryName)).build();
			HttpResponse<String> resp = client.send(request, BodyHandlers.ofString());
		}*/
		/*request = HttpRequest.newBuilder().uri(URI.create("http://localhost:3002/?id="+params.get("id")
		+ "&entry=categories&snd="+this.taskName+"-"+this.entryName)).build();
		HttpResponse<String> resp = client.send(request, BodyHandlers.ofString());*/
		/*request = HttpRequest.newBuilder().uri(URI.create("http://localhost:3001/?id="+params.get("id")
			+ "&entry=categories&snd="+this.taskName+"-"+this.entryName)).build();*/
		Unirest.get(URI.create("http://localhost:3001/?id="+params.get("id")
			+ "&entry=categories&snd="+this.taskName+"-"+this.entryName).toString()).header("Connection", "close").asString();
		//HttpResponse<String> resp = client.send(request, BodyHandlers.ofString());
		
		this.measureIngress();

		if (!this.getLqntask().isEmulated()) {
			this.doWorkCPU();
		} else {
			// get all entry currentyly executing on this task
			Float executing = 0f;
			String[] entries = this.getLqntask().getEntries().keySet().toArray(new String[0]);
			for (String e : entries) {
				// String n = this.getJedis().get(e + "_ex");
				String n = String.valueOf(this.getMemcachedClient().get(e + "_ex"));
				if (n != null) {
					executing += Float.valueOf(n);
				}
			}
			this.doWorkSleep(executing);
		}
		
		this.getLqntask().getRts(entryName).addSample(new rtSample(Long.valueOf(this.getLqntask().getEnqueueTime().get(params.get("id"))),
				System.nanoTime()));

		req.getResponseHeaders().set("Content-Type", "text/html; charset=UTF-8");
		req.getResponseHeaders().set("Cache-Control", "no-store, no-cache, max-age=0, must-revalidate");
		OutputStream outputStream = req.getResponseBody();
		req.sendResponseHeaders(200, renderedTemplate.length());
		outputStream.write(renderedTemplate.getBytes());
		outputStream.flush();
		outputStream.close();
		outputStream = null;

		this.measureEgress();
	}

	@Override
	public String getWebPageName() {
		return "tier1.html";
	}

	@Override
	public String getName() {
		return entryName;
	}
}
