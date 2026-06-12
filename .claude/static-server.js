const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = '/Users/gwchoi/Documents/GitHub/HR_report';
const PORT = 4599;
const TYPES = {'.html':'text/html; charset=utf-8','.png':'image/png','.svg':'image/svg+xml','.json':'application/json','.css':'text/css','.js':'text/javascript'};
http.createServer((req,res)=>{
  let p = decodeURIComponent(req.url.split('?')[0]);
  if(p==='/') p='/index.html';
  const fp = path.join(ROOT,p);
  fs.readFile(fp,(err,data)=>{
    if(err){res.writeHead(404);res.end('not found');return;}
    res.writeHead(200,{'Content-Type':TYPES[path.extname(fp)]||'application/octet-stream'});
    res.end(data);
  });
}).listen(PORT,()=>console.log('static server on '+PORT));
