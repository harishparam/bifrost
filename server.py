from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('runlinks.html')

@app.route('/getlinks')
def getlinks():
    f = open('links.txt', 'r+')
    links=[]
    for line in f:
        links.append(line)
    return json.dumps(links)

# class EmlServer(SMTPServer):
#     no = 0
#     def process_message(self, peer, mailfrom, rcpttos, data):
#         print('Message Received!')
#         filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),
#                 self.no)
#         f = open(filename, 'w')
#         f.write(data)
#         f.close
#         print('%s saved.' % filename)
#         self.no += 1


# def run():
#     foo = EmlServer(('localhost', 25), None)
#     try:
#         asyncore.loop()
#     except KeyboardInterrupt:
#         pass


if __name__ == '__main__':
    app.run(debug=True)