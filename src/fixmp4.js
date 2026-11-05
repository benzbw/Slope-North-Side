/* ใส่ความยาววิดีโอให้ไฟล์ MP4 แบบแบ่งท่อน (fragmented) จาก MediaRecorder — ไม่งั้นบางเครื่องเล่นได้แค่ 1 วิ */
function snsFixMp4(u8){try{var dv=new DataView(u8.buffer,u8.byteOffset,u8.byteLength),L=u8.length;
 function t4(o){return String.fromCharCode(u8[o+4],u8[o+5],u8[o+6],u8[o+7])}
 function sz(o){var s=dv.getUint32(o);if(s==1)s=Number(dv.getBigUint64(o+8));else if(s==0)s=L-o;return s}
 function hdr(o){return dv.getUint32(o)==1?16:8}
 function kids(o,e,fn){var p=o;while(p+8<=e){var s=sz(p);if(s<8||p+s>e)break;fn(p,t4(p),s);p+=s}}
 function find(o,e,ty){var r=-1;kids(o,e,function(p,t){if(r<0&&t==ty)r=p});return r}
 var moov=find(0,L,"moov");if(moov<0)return u8;var mE=moov+sz(moov),mB=moov+hdr(moov);
 var mvhd=find(mB,mE,"mvhd");if(mvhd<0)return u8;var mv=mvhd+8,mvV=u8[mv],mvTS=dv.getUint32(mv+(mvV?20:12));
 var tr={},trex={},absBase=false;
 kids(mB,mE,function(p,t,s){if(t=="trak"){var e=p+s,tk=find(p+8,e,"tkhd"),md=find(p+8,e,"mdia");if(tk<0||md<0)return;var v=u8[tk+8],id=dv.getUint32(tk+8+(v?20:12)),mh=find(md+8,md+sz(md),"mdhd");if(mh<0)return;var mv2=u8[mh+8];
   tr[id]={tkhd:tk,mdhd:mh,ts:dv.getUint32(mh+8+(mv2?20:12)),end:0}}
  if(t=="mvex"){kids(p+8,p+s,function(q,tt){if(tt=="trex"){trex[dv.getUint32(q+12)]=dv.getUint32(q+20)}})}});
 kids(0,L,function(p,t,s){if(t!="moof")return;kids(p+8,p+s,function(q,tt,ss){if(tt!="traf")return;var id=0,dd=0,base=0;
  kids(q+8,q+ss,function(r,ty){var o=r+8,fl=dv.getUint32(o)&0xffffff;
   if(ty=="tfhd"){id=dv.getUint32(o+4);var x=o+8;if(fl&1){absBase=true;x+=8}if(fl&2)x+=4;if(fl&8)dd=dv.getUint32(x);else dd=trex[id]||0}
   if(ty=="tfdt"){base=u8[o]?Number(dv.getBigUint64(o+4)):dv.getUint32(o+4)}
   if(ty=="trun"){var n=dv.getUint32(o+4),x2=o+8,tot=0;if(fl&1)x2+=4;if(fl&4)x2+=4;var per=(fl&0x100?4:0)+(fl&0x200?4:0)+(fl&0x400?4:0)+(fl&0x800?4:0);
    for(var i=0;i<n;i++){tot+=(fl&0x100)?dv.getUint32(x2+i*per):dd}var T=tr[id];if(T)T.end=Math.max(T.end,base+tot);base+=tot}})})});
 var maxMv=0;Object.keys(tr).forEach(function(k){var T=tr[k];if(!T.end||!T.ts)return;var d=Math.round(T.end*mvTS/T.ts);maxMv=Math.max(maxMv,d);
  var mo=T.mdhd+8;if(u8[mo])dv.setBigUint64(mo+24,BigInt(T.end));else dv.setUint32(mo+16,Math.min(T.end,4294967295));
  var to=T.tkhd+8;if(u8[to])dv.setBigUint64(to+28,BigInt(d));else dv.setUint32(to+20,Math.min(d,4294967295))});
 if(!maxMv)return u8;if(mvV)dv.setBigUint64(mv+24,BigInt(maxMv));else dv.setUint32(mv+16,Math.min(maxMv,4294967295));
 /* ใส่ mehd (ความยาวรวมของทุกท่อน) ถ้ายังไม่มี — ทำเฉพาะไฟล์ที่อ้างตำแหน่งข้อมูลจาก moof (ปลอดภัยเมื่อแทรกข้อมูล) */
 var mvex=find(mB,mE,"mvex");if(mvex<0||absBase)return u8;var mehd=find(mvex+8,mvex+sz(mvex),"mehd");
 if(mehd>=0){if(u8[mehd+8])dv.setBigUint64(mehd+12,BigInt(maxMv));else dv.setUint32(mehd+12,Math.min(maxMv,4294967295));return u8}
 if(dv.getUint32(moov)==1||dv.getUint32(mvex)==1)return u8;
 var box=new Uint8Array(20),bd=new DataView(box.buffer);bd.setUint32(0,20);box.set([109,101,104,100],4);bd.setUint32(8,0x01000000);bd.setBigUint64(12,BigInt(maxMv));
 var ins=mvex+8,out=new Uint8Array(L+20);out.set(u8.subarray(0,ins),0);out.set(box,ins);out.set(u8.subarray(ins),ins+20);var od=new DataView(out.buffer);
 od.setUint32(moov,dv.getUint32(moov)+20);od.setUint32(mvex,dv.getUint32(mvex)+20);return out}catch(e){return u8}}
if(typeof module!="undefined")module.exports=snsFixMp4;
