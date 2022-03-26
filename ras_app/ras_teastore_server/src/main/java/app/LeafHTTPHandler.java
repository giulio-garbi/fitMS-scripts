package app;

import java.io.IOException;
import java.io.OutputStream;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.net.http.HttpRequest;
import java.util.Map;

import com.google.common.collect.Maps;
import com.hubspot.jinjava.Jinjava;
import com.sun.net.httpserver.HttpExchange;

import Server.SimpleTask;
import Server.TierHttpHandler;
import monitoring.rtSample;

public class LeafHTTPHandler extends TierHttpHandler {
	
	private final String taskName;
	private String entryName = "";

	public LeafHTTPHandler(SimpleTask lqntask, HttpExchange req, long stime) {
		super(lqntask, req, stime);
		this.taskName = lqntask.getName();
		this.setNC(Main.NC);
	}

	public void handleResponse(HttpExchange req, String requestParamValue) throws InterruptedException, IOException {
		Map<String, String> params = this.getLqntask().queryToMap(req.getRequestURI().getQuery());
		entryName = params.get("entry");
		
		this.measureIngress();

		Jinjava jinjava = new Jinjava();
		Map<String, Object> context = Maps.newHashMap();
		
		context.put("task", taskName);
		context.put("entry", entryName);

		//HttpClient client = null;
		//HttpRequest request = null;
		//client = HttpClient.newBuilder().version(Version.HTTP_1_1).build();

		String renderedTemplate = jinjava.render(this.getWebPageTpl(), context);

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
