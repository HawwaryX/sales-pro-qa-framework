import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.cert.*;
import java.util.*;
import java.util.concurrent.*;
import javax.net.ssl.*;

/** Read-only Android DNS/HTTPS diagnostic. No credentials, response bodies or trust bypass. */
public class NetworkProbe {
    static Map<String,Object> r = Collections.synchronizedMap(new LinkedHashMap<>());
    static volatile String stage = "START";
    static X509TrustManager manager(KeyStore store) throws Exception {
        TrustManagerFactory f=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());f.init(store);
        for (TrustManager t:f.getTrustManagers()) if(t instanceof X509TrustManager)return (X509TrustManager)t;
        throw new GeneralSecurityException("No trust manager");
    }
    static SSLSocketFactory factory(String file) throws Exception {
        if(file.equals("-"))return (SSLSocketFactory)SSLSocketFactory.getDefault();
        final X509TrustManager base=manager(null);
        KeyStore ks=KeyStore.getInstance(KeyStore.getDefaultType());ks.load(null,null);
        try(InputStream in=new FileInputStream(file)){
            int n=0;for(java.security.cert.Certificate c:CertificateFactory.getInstance("X.509").generateCertificates(in))ks.setCertificateEntry("session-ca-"+(n++),c);
        }
        final X509TrustManager extra=manager(ks);
        X509TrustManager combined=new X509TrustManager(){
            public X509Certificate[] getAcceptedIssuers(){return base.getAcceptedIssuers();}
            public void checkClientTrusted(X509Certificate[] c,String a)throws CertificateException{base.checkClientTrusted(c,a);}
            public void checkServerTrusted(X509Certificate[] c,String a)throws CertificateException{
                try{base.checkServerTrusted(c,a);}catch(CertificateException e){extra.checkServerTrusted(c,a);}
            }
        };
        SSLContext context=SSLContext.getInstance("TLS");context.init(null,new TrustManager[]{combined},null);return context.getSocketFactory();
    }
    static String line(InputStream in)throws IOException{
        ByteArrayOutputStream b=new ByteArrayOutputStream();int x;
        while((x=in.read())!=-1){if(x==10)break;if(x!=13)b.write(x);if(b.size()>8192)throw new IOException("Header too large");}
        return b.size()==0&&x==-1?null:b.toString("US-ASCII");
    }
    static int status(String line)throws IOException{
        if(line==null||!line.matches("HTTP/1\\.[01] [0-9]{3}.*"))throw new IOException("No HTTP status line");return Integer.parseInt(line.split(" ")[1]);
    }
    static void headers(InputStream in)throws Exception{String s;while((s=line(in))!=null&&!s.isEmpty()){
        if(s.toLowerCase(Locale.ROOT).startsWith("location:")){
            URI u=new URI(s.substring(9).trim());r.put("redirect_host",u.getHost());r.put("redirect_query_present",u.getRawQuery()!=null);
        }
    }}
    static void execute(String[] a)throws Exception{
        if(a[0].equals("dns")){
            stage="DNS";r.put("hostname",a[1]);
            List<String> addresses=new ArrayList<>();for(InetAddress ip:InetAddress.getAllByName(a[1]))addresses.add(ip.getHostAddress());
            r.put("addresses",String.join(",",addresses));r.put("category","DNS_OK");return;
        }
        URI uri=new URI(a[1]);if(!"https".equals(uri.getScheme())||uri.getUserInfo()!=null||uri.getRawQuery()!=null||uri.getFragment()!=null)throw new IllegalArgumentException("Only credential-free HTTPS URL allowed");
        String host=uri.getHost();r.put("hostname",host);r.put("trust",a[4].equals("-")?"android_default":"android_default_plus_session_CA");
        boolean proxied=!a[2].equals("-");r.put("explicit_managed_proxy",proxied);
        stage=proxied?"PROXY_TCP":"DNS_OR_TCP";
        try(Socket tcp=new Socket()){
            tcp.connect(new InetSocketAddress(proxied?a[2]:host,proxied?Integer.parseInt(a[3]):443),8000);tcp.setSoTimeout(8000);
            if(proxied){
                stage="PROXY_CONNECT";
                tcp.getOutputStream().write(("CONNECT "+host+":443 HTTP/1.1\r\nHost: "+host+":443\r\n\r\n").getBytes(StandardCharsets.US_ASCII));tcp.getOutputStream().flush();
                int code=status(line(tcp.getInputStream()));headers(tcp.getInputStream());r.put("proxy_connect_status",code);
                if(code!=200){r.put("category","PROXY_CONNECT_DENIED");r.put("tls_negotiated",false);return;}
            }
            stage="TLS";
            try(SSLSocket ssl=(SSLSocket)factory(a[4]).createSocket(tcp,host,443,true)){
                ssl.setSoTimeout(8000);SSLParameters p=ssl.getSSLParameters();p.setEndpointIdentificationAlgorithm("HTTPS");p.setServerNames(Collections.singletonList(new SNIHostName(host)));ssl.setSSLParameters(p);
                ssl.startHandshake();r.put("tls_negotiated",true);r.put("tls_protocol",ssl.getSession().getProtocol());r.put("cipher",ssl.getSession().getCipherSuite());
                stage="HTTP";String path=uri.getRawPath();if(path==null||path.isEmpty())path="/";
                ssl.getOutputStream().write(("HEAD "+path+" HTTP/1.1\r\nHost: "+host+"\r\nConnection: close\r\n\r\n").getBytes(StandardCharsets.US_ASCII));ssl.getOutputStream().flush();
                int code=status(line(ssl.getInputStream()));headers(ssl.getInputStream());r.put("origin_http_status",code);r.put("category",code>=400?"ORIGIN_HTTP_ERROR":"HTTPS_OK");
            }
        }
    }
    static String quote(Object o){if(o==null)return "null";if(o instanceof Boolean||o instanceof Number)return o.toString();return "\""+o.toString().replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\"";}
    public static void main(String[] a)throws Exception{
        ExecutorService ex=Executors.newSingleThreadExecutor(task->{Thread t=new Thread(task);t.setDaemon(true);return t;});
        Future<?> future=ex.submit(()->{try{execute(a);}catch(Exception e){
            r.put("error_class",e.getClass().getSimpleName());
            r.put("category",e instanceof UnknownHostException?"DNS_RESOLUTION_FAILURE":e instanceof SSLException?"TLS_FAILURE":e instanceof SocketTimeoutException?"SOCKET_TIMEOUT":"NETWORK_OR_TOOL_FAILURE");
            List<String> causes=new ArrayList<>();for(Throwable t=e;t!=null;t=t.getCause())causes.add(t.getClass().getSimpleName());r.put("cause_classes",String.join(",",causes));
        }});
        try{future.get(22,TimeUnit.SECONDS);}catch(TimeoutException e){r.put("category","TOTAL_TIMEOUT");future.cancel(true);}finally{ex.shutdownNow();}
        r.put("last_stage",stage);StringJoiner j=new StringJoiner(",","{","}");synchronized(r){for(Map.Entry<String,Object> e:r.entrySet())j.add(quote(e.getKey())+":"+quote(e.getValue()));}System.out.println(j);
        System.exit(0);
    }
}
