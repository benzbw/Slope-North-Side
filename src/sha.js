var SHA=(function(){var K=[],H0=[],p=2,n=0;function fr(x){return(x-Math.floor(x))*4294967296|0}
while(n<64){var q=true;for(var d=2;d*d<=p;d++)if(p%d==0){q=false;break}if(q){if(n<8)H0[n]=fr(Math.pow(p,1/2));K[n]=fr(Math.pow(p,1/3));n++}p++}
var W=new Int32Array(64);
function comp(st,b,o){for(var i=0;i<16;i++)W[i]=b[o+i*4]<<24|b[o+i*4+1]<<16|b[o+i*4+2]<<8|b[o+i*4+3];
 for(i=16;i<64;i++){var x=W[i-15],y=W[i-2];W[i]=((x>>>7|x<<25)^(x>>>18|x<<14)^(x>>>3))+W[i-7]+((y>>>17|y<<15)^(y>>>19|y<<13)^(y>>>10))+W[i-16]|0}
 var a=st[0],bb=st[1],c=st[2],dd=st[3],e=st[4],f=st[5],g=st[6],h=st[7];
 for(i=0;i<64;i++){var t1=h+((e>>>6|e<<26)^(e>>>11|e<<21)^(e>>>25|e<<7))+(e&f^~e&g)+K[i]+W[i]|0,t2=((a>>>2|a<<30)^(a>>>13|a<<19)^(a>>>22|a<<10))+(a&bb^a&c^bb&c)|0;h=g;g=f;f=e;e=dd+t1|0;dd=c;c=bb;bb=a;a=t1+t2|0}
 st[0]=st[0]+a|0;st[1]=st[1]+bb|0;st[2]=st[2]+c|0;st[3]=st[3]+dd|0;st[4]=st[4]+e|0;st[5]=st[5]+f|0;st[6]=st[6]+g|0;st[7]=st[7]+h|0}
function hash(msg,st0,pre){var st=st0?Int32Array.from(st0):Int32Array.from(H0),L=msg.length,tot=L+(pre||0),nb=((L+9+63)>>6)<<6,b=new Uint8Array(nb);b.set(msg);b[L]=128;
 var bits=tot*8;for(var i=0;i<4;i++)b[nb-1-i]=bits/Math.pow(2,8*i)&255;for(var o=0;o<nb;o+=64)comp(st,b,o);return st}
function bytes(st){var o=new Uint8Array(32);for(var i=0;i<8;i++){o[i*4]=st[i]>>>24;o[i*4+1]=st[i]>>>16&255;o[i*4+2]=st[i]>>>8&255;o[i*4+3]=st[i]&255}return o}
function pbkdf2(pw,salt,it){var key=pw.length>64?bytes(hash(pw)):pw,ip=new Uint8Array(64),op=new Uint8Array(64);for(var i=0;i<64;i++){ip[i]=(key[i]||0)^54;op[i]=(key[i]||0)^92}
 var si=Int32Array.from(H0),so=Int32Array.from(H0);comp(si,ip,0);comp(so,op,0);
 function hm(m){return bytes(hash(bytes(hash(m,si,64)),so,64))}
 var s1=new Uint8Array(salt.length+4);s1.set(salt);s1[salt.length+3]=1;var u=hm(s1),t=u.slice();for(var k=1;k<it;k++){u=hm(u);for(var j=0;j<32;j++)t[j]^=u[j]}return t}
return{pbkdf2:pbkdf2,hash:function(m){return bytes(hash(m))}}})();
if(typeof module!="undefined")module.exports=SHA;
