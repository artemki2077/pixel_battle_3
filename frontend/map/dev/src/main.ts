import './style.css'


(window as any).mobileCheck = function() {
  let check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||(window as any).opera);
  return check;
};


const HOST = "artemki77.ru";
const IS_SSL = true;
// const HOST = "localhost:8000";
const MIN_WAIT = 1;


interface Cords{
  x: number,
  y: number,
}
interface FetchCell{
  cords: Cords,
  color: string
}

interface Click{
  x: number,
  y: number,
  color: string,
  time: number
}

interface Mouse{
  isDraging: boolean,
  startTouchZoom: number | null,
  moved: boolean;
  touch_zooming: boolean;
  x: number,
  y: number,
}

interface Camera{
  zoom: number,
  lastZoom: number,
  x: number,
  y: number,
}


function getCordsFromString(value: string){
  value = (value as string)!.trim();
  let splited_values = value.split(" ", 2);
  let splited_values_int = splited_values.map((e)=>(parseInt(e)));
  return <Cords>{
    x: splited_values_int[0],
    y: splited_values_int[1],
  }

}

function getEventLocation(e: any) {
  if (e.touches && e.touches.length == 1) {
    return { x: e.touches[0].clientX, y: e.touches[0].clientY };
  } else {
    return { x: e.clientX, y: e.clientY };
  }
}

class Cell{
  x: number;
  y: number;
  cords: Cords;
  color: string;
  size: number;
  constructor(x: number, y: number, color: string, cords: Cords, size: number){
    this.x = x;
    this.y = y;
    this.color = color;
    this.cords = cords;
    this.size = size;
  }

  draw(ctx: CanvasRenderingContext2D){
    ctx.fillStyle = this.color;
    ctx.fillRect(this.cords.x, this.cords.y, this.size, this.size)
  }

  checkMouse(cords: Cords){
    return (
      cords.x > this.cords.x && 
      cords.x < this.cords.x + this.size && 
      cords.y > this.cords.y && 
      cords.y < this.cords.y + this.size
    );
  }
}

class ServerWsConnection{
  socket: WebSocket;
  map: Array<Array<Cell>>
  constructor(map: Array<Array<Cell>>){
    this.map = map;
    this.socket = new WebSocket(`${IS_SSL ? 'wss' : 'ws'}://${HOST}/map/connection`);
    this.socket.onopen = this.onopen.bind(this);
    this.socket.onclose = this.onclose.bind(this);
    this.socket.onmessage = this.onmessage.bind(this);
    this.socket.onerror = this.onerror.bind(this);
  }
  onopen(){
    console.log("ws connected");
  }

  onclose(event: CloseEvent){
    this.socket = new WebSocket(`${IS_SSL ? 'wss' : 'ws'}://${HOST}/map/connection`);
    this.socket.onopen = this.onopen.bind(this);
    this.socket.onclose = this.onclose.bind(this);
    this.socket.onmessage = this.onmessage.bind(this);
    this.socket.onerror = this.onerror.bind(this);
    console.log(event);

  }
  onerror(event: Event){
    console.log("error ws");
    console.error(event);
  }
  onmessage(event: MessageEvent){
    // console.log(event);
    let click_json = JSON.parse(event.data);
    let click = <Click>{
      x: click_json.x,
      y: click_json.y,
      color: click_json.color,
      time: Date.parse(click_json.time)
    }
    this.map[click.y][click.x].color = click.color;
  }
}

class Map{
  area: Array<Array<Cell>>;
  size: number;
  cords: Cords;
  server: ServerWsConnection;
  constructor(size: number, cords: Cords){
    this.cords = cords;
    this.size = size;
    let count_cell = 50;
    this.area = Array.from(Array(count_cell).keys()).map((y)=>Array.from(Array(count_cell).keys()).map((x)=>new Cell(x, y, "#ffffff", {x: cords.x + (x * size / count_cell), y: cords.y + (y * (size / count_cell))}, size / count_cell)));
    this.server = new ServerWsConnection(this.area);
    // let cors: Array<Cords> =[
    //   {x: 19, y: 19},
    //   {x: 20, y: 20},
    //   {x: 21, y: 21},
    //   {x: 22, y: 22},
    //   {x: 23, y: 23},
    //   {x: 24, y: 24},
    //   {x: 19, y: 18},
    //   {x: 15, y: 18}
    // ];
    // for(let cord  of cors){
    //   this.area[cord.y][cord.y].color = "#ff0000";
    // }
  }
  draw(ctx: CanvasRenderingContext2D){
    ctx.fillStyle = "#fff";
    ctx.fillRect(this.cords.x, this.cords.y, this.size, this.size);
    this.area.forEach((e)=>{
      e.forEach((cell: Cell)=>{
        cell.draw(ctx);
      })
    })
  }

  getCellByCords(cords: Cords){
    return this.area[cords.y][cords.x]
  }
}
class Cursor extends Cell{
  activate: boolean;
  constructor(cords: Cords, size: number){
    super(0, 0, "rgba(0, 0, 0, 0.3)", cords, size);
    this.activate = false;
  }
}

class World{
  mouse: Mouse;
  camera: Camera;
  SCROLL_SENSITIVITY: number;
  cursor: Cursor;
  selectedColor: string;
  isMobile: boolean;
  lastClick: number;
  map: Map;
  MIN_ZOOM: number;
  MAX_ZOOM: number;
  cnv: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;

  constructor(){
    this.selectedColor = "#000000";
    this.lastClick = Date.now();
    this.cnv = <HTMLCanvasElement> document.getElementById("cnv");
    this.ctx = <CanvasRenderingContext2D> this.cnv.getContext("2d");
    this.cnv.width = window.innerWidth;
    this.cnv.height = window.innerHeight;
    this.SCROLL_SENSITIVITY = 0.001;
    this.isMobile = (window as any).mobileCheck();
    this.MAX_ZOOM = 20;
    this.MIN_ZOOM = 0.7;
    let cnv_size = Math.min(this.cnv.width, this.cnv.height) * 0.9;
    this.map = new Map(
      cnv_size,
      {
        x: (this.cnv.width / 2) - (cnv_size / 2),
        y: (this.cnv.height / 2) - (cnv_size / 2)
      }
    );
    this.loadMap();
    this.cursor = new Cursor({x: (this.cnv.width / 2) - (cnv_size / 2), y: (this.cnv.height / 2) - (cnv_size / 2)}, cnv_size / 50);
    this.mouse = {
      moved: false,
      isDraging: false,
      startTouchZoom: null,
      touch_zooming: false,
      x: 0,
      y: 0,
    };
    this.camera = {
      zoom: 1,
      lastZoom: 1,
      x: 0,
      y: 0,
    }
  }

  async click(cell: Cell){
    let response: Response = await fetch(
      `${IS_SSL ? 'https' : 'http'}://${HOST}/map/click`,
      {
        method: "POST",
        credentials: "same-origin",
        body: JSON.stringify(
          {
            x: cell.x,
            y: cell.y,
            color: this.selectedColor,
          }
        ),
      }
    );
    let data = await response.json();
    if(data.ok == false && data.result == "wait"){
      console.log(this.lastClick);
      this.lastClick = new Date(data.last_click).getTime();
      console.log(this.lastClick);
      alert(`Ваше время заморозки ещё не прошло, у вас ещё ${data.time_left} секунд`);
      return;
    }
    if (data.ok == undefined || !data.ok || data.ok == null){
      alert(`чёт на сайте сломалось при попытке нажать, напишите об этом @artemki77 ошибка: ${JSON.stringify(data)}`);
      return;
    }
    if(data.ok){
      this.lastClick = Date.now();
    }
  }

  updateTimer(){
    let milisec = (this.lastClick - Date.now());
    milisec = (MIN_WAIT * 60 * 1000) + milisec;
    // console.log(milisec / 1000);
    if(milisec <= 0){
      
      document.getElementById("timeLeft")!.innerHTML = `00:00`;
      return;
    }
    let waitSec = (Math.floor((milisec / 1000)) % 60).toString();
    let waitMin = (Math.floor((milisec / 1000) / 60) % 60).toString();
    waitSec = waitSec.length == 1 ? `0${waitSec}` : waitSec;
    waitMin = waitMin.length == 1 ? `0${waitMin}` : waitMin;

    document.getElementById("timeLeft")!.innerHTML = `${waitMin}:${waitSec}`;
  }

  async loadMap(){
    let response: Response = await fetch(
      `${IS_SSL ? 'https' : 'http'}://${HOST}/map/all_map`,
      {
        method: "GET",
        credentials: "same-origin"
      }
    )
    let data: any = await response.json()
    if(data == null || data == undefined || !data || !data.ok){
      console.log(data);
      alert(`произошла ошибка при прогрузке карты, попробуйте перезагрузить сайт, если не поможет напишите об этом @artemki77, ошибка: ${JSON.stringify(data)}`)
      return
    }
    let cells: Array<FetchCell> = [];
    data.result.map((e: any)=>{
      e.cords = getCordsFromString(e.cords);
      cells.push(e);
    });
    this.lastClick = Date.parse(data.last_click);
    
    for(let cell of cells){
      this.map.area[cell.cords.y][cell.cords.x].color = cell.color;
    }
  }

  touch(e: TouchEvent | MouseEvent, heandler: any){
    if((e as TouchEvent).touches.length != 1 && (e as TouchEvent).type == "touchstart"){
      this.mouse.touch_zooming = true;
    }
    if ((e as TouchEvent).touches.length == 1) {
      heandler(e);
    }else if((e as TouchEvent).touches.length == 2 && (e as TouchEvent).type == "touchmove"){
      this.mouse.isDraging = false;
      this.touchZoom(e as TouchEvent);
    }
  }

  touchZoom(e: TouchEvent){
    e.preventDefault();

    let touch1 = <Cords>{x: e.touches[0].clientX, y: e.touches[0].clientY};
	  let touch2 = <Cords>{x: e.touches[1].clientX, y: e.touches[1].clientY};

    let distanceTouches = (touch1.x - touch2.x) ** 2 + (touch1.y - touch2.y) ** 2;

    if(this.mouse.startTouchZoom == null){
      this.mouse.startTouchZoom = distanceTouches;
    }else{
      if (!this.mouse.isDraging)
        {
            this.camera.zoom = (distanceTouches / this.mouse.startTouchZoom) * this.camera.lastZoom
            this.camera.zoom = Math.min( this.camera.zoom, this.MAX_ZOOM )
            this.camera.zoom = Math.max( this.camera.zoom, this.MIN_ZOOM )
        }
    }
  }

  touchDown(e: TouchEvent | MouseEvent){
    this.touch(e, this.mouseDowm.bind(this));
  }

  touchMove(e: TouchEvent | MouseEvent){
    this.touch(e, this.mouseMove.bind(this));
  }

  touchUp(e: TouchEvent | MouseEvent){
    this.camera.lastZoom = this.camera.zoom;
    this.touch(e, this.mouseUp.bind(this));
  }

  mouseDowm(e: MouseEvent){
    this.mouse.moved = false;
    this.mouse.isDraging = true;
    this.mouse.x = getEventLocation(e).x / this.camera.zoom - this.camera.x;
	  this.mouse.y = getEventLocation(e).y / this.camera.zoom - this.camera.y;
  }
  
  mouseMove(e: MouseEvent){
    if(this.mouse.isDraging){
      this.mouse.moved = true;
      this.camera.x = getEventLocation(e).x / this.camera.zoom - this.mouse.x;
  		this.camera.y = getEventLocation(e).y / this.camera.zoom - this.mouse.y;
    }
    let xOfMap = (getEventLocation(e).x - this.cnv.width / 2) / this.camera.zoom + window.innerWidth / 2 - this.camera.x;
    let yOfMap = (getEventLocation(e).y - this.cnv.height / 2) / this.camera.zoom + window.innerHeight / 2 - this.camera.y;
    let cursorInMap = false
    for(let y_array of this.map.area){
      for(let cell of y_array){
        if(cell.checkMouse({x: xOfMap, y: yOfMap})){
          cursorInMap = true;
          this.cursor.activate = true;
          this.cursor.x = cell.x;
          this.cursor.y = cell.y;
          this.cursor.cords = cell.cords;
          break;
        }
      }
    }
    if(!cursorInMap){
      this.cursor.activate = false;
    }
  }

  mouseUp(e: MouseEvent){
    this.mouse.isDraging = false;
    this.mouse.startTouchZoom = null;

    if(!this.mouse.moved && !this.mouse.touch_zooming){
      let xOfMap = (getEventLocation(e).x - this.cnv.width / 2) / this.camera.zoom + window.innerWidth / 2 - this.camera.x;
      let yOfMap = (getEventLocation(e).y - this.cnv.height / 2) / this.camera.zoom + window.innerHeight / 2 - this.camera.y;

      for(let y_array of this.map.area){
        for(let cell of y_array){
          if(cell.checkMouse({x: xOfMap, y: yOfMap})){
            // cursorInMap = true;
            // this.cursor.activate = true;
            // this.cursor.x = cell.x;
            // this.cursor.y = cell.y;
            // this.cursor.cords = cell.cords;
            this.click(cell);
            break;
          }
        }
      }
      
    }

    this.mouse.moved = false
    this.mouse.touch_zooming = false;
  }

  zoomCamera(zoomAmount: number){
    if (!this.mouse.isDraging)
      {
          this.camera.zoom += zoomAmount
          this.camera.zoom = Math.min( this.camera.zoom, this.MAX_ZOOM )
          this.camera.zoom = Math.max( this.camera.zoom, this.MIN_ZOOM )
      }
  }

  draw(){
    this.cnv.width = window.innerWidth;
    this.cnv.height = window.innerHeight;

    // routing in map
    this.ctx.translate(window.innerWidth / 2, window.innerHeight / 2);
    this.ctx.scale(this.camera.zoom, this.camera.zoom);
    this.ctx.translate(
      -window.innerWidth / 2 + this.camera.x,
      -window.innerHeight / 2 + this.camera.y
    );
    // end routing in map

    this.ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

    this.map.draw(this.ctx);
    if(!this.isMobile && this.cursor.activate){
      this.cursor.draw(this.ctx);
    }
    requestAnimationFrame(this.draw.bind(this));
  }
}


let world = new World();
world.draw();

world.cnv.addEventListener("wheel", (e) => world.zoomCamera(-e.deltaY * world.SCROLL_SENSITIVITY));
world.cnv.addEventListener("mousedown", world.mouseDowm.bind(world));
world.cnv.addEventListener("mousemove", world.mouseMove.bind(world));
world.cnv.addEventListener("mouseup", world.mouseUp.bind(world));
world.cnv.addEventListener("touchstart", world.touchDown.bind(world));
world.cnv.addEventListener("touchmove", world.touchMove.bind(world));
world.cnv.addEventListener("touchend", world.touchUp.bind(world));


setInterval(()=>{world.updateTimer();}, 1000);

let colors = [
	"#FFA500", "#664200", "#331a00", "#00fac8", "#009476", "#9600c8", "#490061", "#e1beaa", "#c4845e", 
	"#ffaabe", "#ff5f82", "#000000", "#808080", "#C0C0C0", "#FFFFFF", "#FF00FF", "#800080", "#FF0000", 
	"#800000", "#FFFF00", "#808000", "#00FF00", "#008000", "#00FFFF", "#008080", "#0000FF", "#000080", 
	"#FA8750", "#ffd700"
]
let colors_elem = <HTMLElement> document.getElementById("colors");
let selected_color_elem = <HTMLAnchorElement> document.getElementById("selectedColor");
selected_color_elem.style.backgroundColor = "#000000";
colors.forEach((e)=>{
  let new_color_elem = document.createElement("div")
  new_color_elem.classList.add("color")
  new_color_elem.style.backgroundColor = e;
  new_color_elem.onclick = ()=>{
    world.selectedColor = e;
    selected_color_elem.style.backgroundColor = e;
  }
  colors_elem.append(new_color_elem);
})
