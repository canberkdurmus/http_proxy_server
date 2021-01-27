# HTTP Server & Proxy Server


## Overview

For the implementations of the HTTP server and proxy server, Python 3 programming language is used with socket, os, threading, argparse libraries. There is no other library that has been used like HTTP or Requests.


## HTTP SERVER

1. **Multithreading:** After starting to listen to the given port; when a connection arrives, another thread is created with the current connection object. Main thread is in an endless loop, constantly listening to the port and creating new threads for new connections. Rest of the process will be continued on that thread like parsing the request, preparing the response etc. After the process is complete, the created thread sends the response to the client and returns. Below you can see the creation of the thread.

![](./img/Report.005.png)

![](./img/Report.006.png)

![](./img/Report.007.png)


3. **Generating and Returning HTML Files or Error Pages:** When a request arrives, a “Request” object is created. In the constructor of the Request class; it gets separated by it’s lines and after that HTTP method and the path is extracted as object attributes so they can be accessed later for error check mechanisms. See below the constructor:

![](./img/Report.008.png)

After the creation of the Request object, it is sent to the ‘generate\_response’ method, obviously this is the method which generates the response as html file, error or any legal response type. The method returns a body and status code. See below:

![](./img/Report.009.png)

generate\_response method basically checks for any erroneous status for request and generates the response accordingly. In the first step it checks if the HTTP Method is GET or not; if it is not, it checks the validity of the HTTP method. If it is valid but not GET returns ‘501 Not Implemented’ code with a small html string. If it is not GET and it is invalid it returns ‘400 Bad Request”

In the next step the method tries to cast the request path to integer, if it gives an error the method returns a ‘400 Bad Request’ but with a different and explanatory error response page. If it is an integer but it is not between 100 and 20000, it returns the same error code with other explanatory error response pages.

In the last step the response file string is generated between the HTML tags. The pages with only html tags are seems valid for modern browsers so we didn’t add any body, head or other tags to keep the response simple. Every character in the response is one byte so “(requested size) - (total html tag length)” will give the characters to add to the string. The generation part is really far from any performance optimizations, we could generate or load one max sized string (20000) at the beginning of the main thread and after that we could trim it as given size to respond fast but we wanted to make calculations a bit hard to make for the server and see the benchmark results. After the generation of the final string method returns with ‘200 OK’ response code and the generated string. Below, response code and error page contents can be seen:

![](./img/Report.010.png)

4. **Response Line and Headers:** The server generates the headers after the generation of the response (error page or generated file) with get\_header method. The method takes a response code and content length as arguments and generates the headers according to them. Below, the method can be seen:

![](./img/Report.011.png)

While the generation of the headers, method use Statuses dictionary to get the proper status message for the status code. The first line of the response header contains the HTTP version, status code and status message. The second line contains the Content-Type as requested and the third line contains the Content-Length header which is equal to the requested path.

5. **Not Int, Greater Than 20000, Lower Than 100:** While generating the response, the server checks the path if the requested file size is greater than 20000 or less than 100.

![](./img/Report.012.png)

If the requested file size is greater than 20000 or less than 100, ‘400 Bad Request’ returns with a HTML page which notifies the user about the error. This case is also valid for non integer requests. See Below:

![](./img/Report.013.png)

6. **Printing Received and Sent Messages:** The HTTP server prints every message that it received from the port and every message that it generated and sent to the terminal. See below:

![](./img/Report.014.png)

7. **Connection with a Browser:** Browser interaction of the server can be seen with examples below:

![](./img/Report.015.png)

![](./img/Report.016.png)

![](./img/Report.017.png)![](./img/Report.018.png)


## PROXY SERVER

1. **Relaying Traffic Between Client and HTTP Server:** Proxy server instances are created just like the HTTP server instances at the beginning. After the creation of the Proxy server instance, it initiates a proxy\_socket object and all traffic will be flowing on it.

![](./img/Report.019.png)

While listening to the given port, the thread is in an endless loop and if any connection arrives, the main thread creates a new thread that will take over the client process.

![](./img/Report.020.png)

In the response method data is received from the new connection, a ProxyRequest object is initialized with the data and response is prepared with the ‘server\_side’ method. After the response is provided from the server side, it is sent to the client.

![](./img/Report.021.png)

In the ‘server\_side’ method the traffic is relayed to the HTTP server after the required error checks (>9999 error, 404 Not Found etc.) and processes (caching, conditional GET etc.) Only the relay part of the ‘server\_side’ method can be seen below:

![](./img/Report.022.png)

2. **Using Port 8888, Any Client is Able to Send GET:** Port is set by the user at the execution line of the program, see below:

After the initialization of the proxy server, network traffic of the computer should be ![](./img/Report.023.png)pointed to the proxy server. Every OS has its own system-wide proxy settings interface and almost any modern browser won’t override the system proxy, they open system proxy settings instead of providing another proxy setting.


![](./img/Report.024.png)

System proxy settings can be changed in Mac OS X (left) and Ubuntu 18.04 (right) as below:

![](./img/Report.025.png)![](./img/Report.026.png)

Both of them have ‘localhost, 127.0.0.0/8, ::1’ hosts in the ignore/bypass list by default but removing them has no effect for directing the ‘localhost’ traffic to the custom proxy, request would go to the HTTP server without visiting the proxy server. We built a small work around for this issue. Requesting a dummy hostname like ‘testlocal’ and when it arrives at the proxy, changing it to ‘localhost’ makes it possible to make the localhost traffic relayed on the proxy server. See below (In the ProxyRequest class ):

![](./img/Report.027.png)

3. **Directing Only to the HTTP Server:** The proxy server relays the traffic to the required host, it won't generate any files instead of the HTTP server or do anything else on behalf of the HTTP server.
4. **Limiting Requests with Maximum URL /9999:** In the ‘server\_side’ method, the request path is checked if it is greater than 9999. If it is, the proxy server returns ‘414 URI Too Long’ error message with 414 HTTP status code.

![](./img/Report.028.png)

5. **404 Not Found Support:** In the ‘server\_side’ method, the proxy server tries to connect to the requested host. If there is a connection error, the proxy server returns a ‘404 Not Found’ message with 404 HTTP status code.

![](./img/Report.029.png)

6. **Proxy Server Should Be Accessible with Proxy Settings:** As we explained in the ‘Section B’, it can be accessed as ‘localhost’ if the system won’t override the ‘localhost’ hostname, if it is overridden it also can be reached as ‘testlocal’. See below:

![](./img/Report.030.png)

![](./img/Report.031.png)

HTTP Server process cancelled:

![](./img/Report.032.png)

7. **Bonus Cache:** There is a dictionary of the ‘socket\_manager’ to keep cached responses for older requests. When a new request arrives it is checked and if there is no response in the cache that fits to the request it is fetched from the HTTP server and added to the cache dictionary. If there is a cached suitable response in the cache it is returned to the client without asking the HTTP server. See the cache check and add lines below:

![](./img/Report.033.png)

Cache operations are done by two methods below:

![](./img/Report.034.png)

8. **Bonus Conditional GET:** Conditional GET header is checked in the ProxyRequest object as below and set a flag if a Conditional GET header exists:

![](./img/Report.035.png)

While generating the response in the ‘server\_side’ method, if conditional GET flag is set for the request object and if the requested path is even; ‘304 Not Modified’ is sent to the client, see below:
![](./img/Report.036.png)

Using ApacheBench (ab) program



||**a**|**b**|**c**|**a (k)**|**b (k)**|**c (k)**|
| :- | - | - | - | - | - | - |
||**-n 10 -c 1**|**-n 10 -c 5**|**-n 10 -c 10**|**-n 10 -c 1 -k**|**-n 10 -c 5 -k**|**-n 10 -c 10 -k**|
|**Time taken for tests (s)**|46.531|17.385|12.324|35.938|20.273|13.563|
|**Total transferred (bytes)**|52431510|52431510|52431510|52431560|52431560|52431560|
|**HTML transferred (bytes)**|52428800|52428800|52428800|52428800|52428800|52428800|
|**Time per request\* (ms)**|4653.128|1738.507|1232.431|3593.841|2027.289|1356.259|
|**Requests per sec (#/s)**|0.21|0.58|0.81|0.28|0.49|0.74|
|**Transfer rate (Kbytes/s)**|1100.39|2945.21|4154.61|1424.73|2525.67|3775.29|
|**Conn Time (Connect) (ms)**|75|187|87|8|42|76|
|**Conn Time (Processing) (ms)**|4578|7644|9470|3586|8508|9156|
|**Conn Time (Waiting) (ms)**|76|78|79|75|89|78|
|**Conn Time (Total) (ms)**|4653|7831|9557|3594|8550|9232|
\* Across all concurrent requests

**Conclusions:**

- Keep-Alive header makes a major improvement if the job is not very concurrent because there is no new connection required for every request. When the concurrency of the job is high (for example sending all 10 requests at the same time) keep-alive almost no effect because when a new request arrives and the old connection is not done yet, a new connection is established.
- Shortest test time belongs to full concurrent 10 requests. This option has more Connection Time for requests because every request opens a new connection and the server is trying to serve 10 concurrent requests but this one has the best overall test time.


- Shortest connection time (per request) belongs to synchronous 10 requests with keep alive header because *connect* takes almost no time thanks to the keep alive and *processing* time is better because server is nor overwhelmed by ten concurrent requests.

Testing Our Server Using ApacheBench



|**N = 5000**|c = 1|c=10|c=100|c= 250|c=500|c=1000|
| - | - | - | - | - | - | - |
|**Transferred (bytes)**|500000|500000|500000|500000|500000|500000|
|**Time Per Req (ms)**|0.230|0.237|0.246|0.295|0.302|2.210|
|**Requests per s (#/s)**|4925.41|4104.23|4058.16|3393.21|3316.54|452.52|


![](./img/Report.037.png)
