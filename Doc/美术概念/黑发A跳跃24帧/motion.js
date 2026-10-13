// Fixed-height vertical motion, independent horizontal steering.
const JumpMotion = {
 height:140, gravity:1400,
 get duration(){return 2*Math.sqrt(2*this.height/this.gravity)},
 sample(t){const v=Math.sqrt(2*this.height*this.gravity);return Math.max(0,v*t-.5*this.gravity*t*t)},
 horizontal(x,axis,dt){return Math.max(70,Math.min(890,x+axis*230*dt))}
};
if(typeof module!=='undefined')module.exports=JumpMotion;
