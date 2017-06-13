http_header = '''HTTP/1.1 200 OK
Content-Type: text/html
Connection: close
'''

def get_network_setup_html(sta):

    available_networks = []
    for item in sta.scan():
        available_networks.append(item[0])

    options = ''
    for network_name in available_networks:
        network_name = network_name.decode()
        options += '''<option value='{0}'>{1}</option>
                                    '''.format(network_name, network_name)

    html = '''
        <html>
            <body>
                <form method="POST">
                    <table>
                        <h1>Welcome to the uPy setup screen.</h1>
                        <h3>Select a network to connect your uPy to.</h3>
                        <br><br>
                        <tr>
                            <td>Select SSID:</td>
                            <td>
                                <select name="SSID">
                                    {0}
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>Password:</td>
                            <td><input type="password" name="Password"></td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <input type="submit" value="Connect Now">
                            </td>
                        </tr>
                    </table>
                </form>
            </body>
        </html>

'''.format(options)

    return make_http_response(http_header, html)

def make_http_response(header, body):
    return header + body