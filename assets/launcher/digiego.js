/* DigiEgo: offline personality, moments and bond minigame. Independent from main-game stats. */
(() => {
  'use strict';
  const KEY = 'digirogue-digiego-v1';
  const BUDDIES_KEY = 'digirogue-buddies';
  const looks = {sky:{skin:'#d7a574',hair:'#382a42',shirt:'#3aa6be',trim:'#f6d565'},sun:{skin:'#f0c08a',hair:'#70402e',shirt:'#e5a943',trim:'#e65b52'},forest:{skin:'#c98965',hair:'#272d3b',shirt:'#53a96b',trim:'#f5da72'},flame:{skin:'#edb188',hair:'#a43d43',shirt:'#da554e',trim:'#f2c35d'},tide:{skin:'#d99c79',hair:'#3c3155',shirt:'#386ac4',trim:'#61d5cf'},moon:{skin:'#e6bd96',hair:'#292c4b',shirt:'#794fb4',trim:'#f190b7'}};
  const species = [
    {id:'agumon',name:'Agumon',stage:'Rookie',trait:{es:'valiente, curioso e impulsivo',en:'brave, curious and impulsive'},quip:{es:'Si hay algo nuevo, quiero verlo primero.',en:'If something is new, I want to see it first.'},asset:'assets/launcher/digimon/agumon.png'},
    {id:'gabumon',name:'Gabumon',stage:'Rookie',trait:{es:'reservado, leal y atento',en:'quiet, loyal and observant'},quip:{es:'No hace falta decir mucho cuando estás aquí.',en:'We do not need many words when you are here.'},asset:'assets/launcher/digimon/gabumon.png'},
    {id:'patamon',name:'Patamon',stage:'Rookie',trait:{es:'optimista, juguetón y cariñoso',en:'optimistic, playful and affectionate'},quip:{es:'¡Vamos a descubrir algo bonito!',en:'Let us go find something lovely!'},asset:'assets/launcher/digimon/patamon.png'},
    {id:'koromon',name:'Koromon',stage:'In-Training',trait:{es:'mimoso, inquieto y muy curioso',en:'cuddly, restless and very curious'},quip:{es:'¿Y eso? ¿Y aquello? ¡Quiero verlo todo!',en:'What is that? And that? I want to see it all!'},asset:'assets/launcher/digimon/koromon.png'},
    {id:'greymon',name:'Greymon',stage:'Champion',trait:{es:'orgulloso, protector y noble',en:'proud, protective and noble'}},
    {id:'garurumon',name:'Garurumon',stage:'Champion',trait:{es:'sereno, independiente y vigilante',en:'calm, independent and watchful'}},
    {id:'angemon',name:'Angemon',stage:'Champion',trait:{es:'compasivo, paciente y solemne',en:'compassionate, patient and solemn'}},
    {id:'tokomon',name:'Tokomon',stage:'In-Training',trait:{es:'alegre, expresivo y pegajoso',en:'cheerful, expressive and clingy'}},
    {id:'biyomon',name:'Biyomon',stage:'Rookie',trait:{es:'sociable, decidida y luminosa',en:'sociable, determined and bright'}},
    {id:'tentomon',name:'Tentomon',stage:'Rookie',trait:{es:'analítico, ingenioso y paciente',en:'analytical, witty and patient'}},
    {id:'palmon',name:'Palmon',stage:'Rookie',trait:{es:'dulce, firme y protectora',en:'gentle, steadfast and protective'}},
    {id:'gomamon',name:'Gomamon',stage:'Rookie',trait:{es:'bromista, aventurero y despreocupado',en:'mischievous, adventurous and carefree'}},
    {id:'gatomon',name:'Gatomon',stage:'Champion',trait:{es:'orgullosa, perspicaz y afectuosa',en:'proud, perceptive and affectionate'}},
    {id:'veemon',name:'Veemon',stage:'Rookie',trait:{es:'competitivo, valiente y cercano',en:'competitive, brave and warm'}},
    {id:'wormmon',name:'Wormmon',stage:'Rookie',trait:{es:'tímido, sensible y fiel',en:'shy, sensitive and devoted'}},
    {id:'renamon',name:'Renamon',stage:'Rookie',trait:{es:'silencioso, intuitivo y disciplinado',en:'quiet, intuitive and disciplined'}},
    {id:'demidevimon',name:'DemiDevimon',stage:'Rookie',trait:{es:'travieso, teatral y más tierno de lo que admite',en:'mischievous, dramatic and softer than it admits'}}
  ];
  const copy = {
    es:{
      title:'DigiEgo: tu compañero tiene vida propia',subtitle:'Un minijuego de compañía, recuerdos y vínculo. Todo ocurre aquí, sin conexión.',
      badge:'MINIJUEGO OFFLINE',tamerTitle:'CREA TU TAMER',tamerName:'NOMBRE DEL TAMER',tamerLook:'ELIGE TU ASPECTO',createTamer:'CREAR TAMER',editTamer:'CAMBIAR',tamerHelp:'Tu tamer y DigiEgo se guardan en este navegador, aparte de las partidas.',tamerReady:'TAMER CREADO',createTamerFirst:'Crea tu tamer para empezar.',lookSky:'CIELO',lookSun:'SOL',lookForest:'BOSQUE',lookFlame:'FUEGO',lookTide:'MAREA',lookMoon:'LUNA',partner:'COMPAÑERO',trait:'CARÁCTER',bond:'VÍNCULO',gift:'A partir de tres corazones empieza a traerte pequeños regalos.',carry:'Al completar el vínculo, un corazón quedará para el próximo huevo.',
      talk:'Hablar',praise:'Elogiar',scold:'Regañar',pet:'Acariciar',greet:'¡Hola! ¿Qué hacemos juntos?',
      memory:'MEMORIAS COMPARTIDAS',life:'Una vida antes de conocerte',empty:'Aún no hay recuerdos. Elige un momento para empezar vuestra historia.',
      moments:'MOMENTOS',cold:'Freezeland · con frío',race:'Una carrera hasta la palmera',win:'Después de ganar',farewell:'La despedida',
      coldLine:'El viento helado nos empuja, pero no pienso soltarte la mano.',raceLine:'¡A la cuenta de tres! Esta vez voy a ganar yo.',winLine:'Lo hicimos juntos. Esa es mi parte favorita de ganar.',farewellLine:'Aunque el camino se separe, guardaré cada momento contigo.',
      hinted:'Hay algo moviéndose más allá del bosque… pronto sabremos qué es.',giftLine:'Te guardé un pequeño regalo de nuestro paseo.',scoldLine:'No me ha gustado mucho eso… pero sé que podemos volver a empezar.',
      talkLine:'Me gusta cuando nos quedamos un rato juntos.',praiseLine:'¿De verdad piensas eso de mí? ¡Ahora quiero esforzarme aún más!',petLine:'Mmm… así está bien. No pares todavía.',
      before:'Antes de encontrarte, soñaba con un lugar donde nadie tuviera que estar solo.',
      language:'IDIOMA DE LOS DIÁLOGOS',enabled:'DigiEgo activo',disabled:'DigiEgo apagado',english:'ENGLISH',spanish:'ESPAÑOL',off:'APAGAR',on:'ENCENDER',
      stored:'Los recuerdos se guardan en este navegador, separados de tus estadísticas y partidas.',hearts:'corazones',recorded:'Recuerdo guardado',newBuddy:'Elige un compañero que hayas descubierto en la Digidex.',
      sceneDone:'Momento vivido',hintLabel:'PISTA',pick:'Elige un momento para compartirlo.'
    },
    en:{
      title:'DigiEgo: your partner has a life of its own',subtitle:'A little companion game about memories and bond. It all happens here, offline.',
      badge:'OFFLINE MINIGAME',tamerTitle:'CREATE YOUR TAMER',tamerName:'TAMER NAME',tamerLook:'CHOOSE YOUR LOOK',createTamer:'CREATE TAMER',editTamer:'EDIT',tamerHelp:'Your tamer and DigiEgo are saved in this browser, separately from game runs.',tamerReady:'TAMER CREATED',createTamerFirst:'Create your tamer to begin.',lookSky:'SKY',lookSun:'SUN',lookForest:'FOREST',lookFlame:'FIRE',lookTide:'TIDE',lookMoon:'MOON',partner:'PARTNER',trait:'PERSONALITY',bond:'BOND',gift:'At three hearts, your partner starts bringing little gifts.',carry:'Complete the bond and one heart will carry to the next egg.',
      talk:'Talk',praise:'Praise',scold:'Scold',pet:'Pet',greet:'Hey! What should we do together?',
      memory:'SHARED MEMORIES',life:'A life before you met',empty:'No memories yet. Pick a moment to begin your story.',
      moments:'MOMENTS',cold:'Freezeland · feeling chilly',race:'A race to the palm tree',win:'After a victory',farewell:'The farewell',
      coldLine:'The icy wind is strong, but I am not letting go of your hand.',raceLine:'Ready, set, go! I am going to win this time.',winLine:'We did it together. That is my favorite part of winning.',farewellLine:'Even if our paths part, I will keep every moment with you.',
      hinted:'Something is moving beyond the forest… soon we will find out.',giftLine:'I saved a little gift from our walk for you.',scoldLine:'I did not love that… but we can always start again.',
      talkLine:'I like it when we take a little time to be together.',praiseLine:'You really think that? Now I want to try even harder!',petLine:'Mmm… that feels nice. Do not stop yet.',
      before:'Before I met you, I dreamed of a place where nobody had to be alone.',
      language:'DIALOGUE LANGUAGE',enabled:'DigiEgo is on',disabled:'DigiEgo is off',english:'ENGLISH',spanish:'ESPAÑOL',off:'TURN OFF',on:'TURN ON',
      stored:'Memories stay in this browser, separate from your game stats and runs.',hearts:'hearts',recorded:'Memory saved',newBuddy:'Choose a partner you have discovered in the Digidex.',
      sceneDone:'Moment shared',hintLabel:'A HUNCH',pick:'Choose a moment to share.'
    }
  };
  const read = (key, fallback) => {try {const value=JSON.parse(localStorage.getItem(key)); return value && typeof value==='object' ? value : fallback;} catch (_) {return fallback;}};
  const write = value => {try {localStorage.setItem(KEY,JSON.stringify(value));} catch (_) {}};
  const defaultData = () => ({version:1,language:'en',enabled:true,selected:'agumon',carryover:0,partners:{},interactions:0});
  let data = Object.assign(defaultData(), read(KEY,{}));
  data.partners = data.partners && typeof data.partners==='object' ? data.partners : {};
  data.tamer = data.tamer && typeof data.tamer==='object' ? data.tamer : null;
  let draftLook = data.tamer?.look || 'sky';
  let draftName = data.tamer?.name || '';
  const byId = id => species.find(item=>item.id===id) || species[0];
  function discovered(){
    const found = new Set(['agumon']);
    const buddies = read(BUDDIES_KEY,[]);
    (Array.isArray(buddies)?buddies:[]).forEach(id=>found.add(String(id).toLowerCase()));
    return species.filter(item=>found.has(item.id));
  }
  function partnerState(id){
    if(!data.partners[id]) data.partners[id]={bond:Math.max(0,Math.min(100,Number(data.carryover)||0)),memories:[],giftClaimed:false};
    const saved=data.partners[id];
    saved.bond=Math.max(0,Math.min(100,Number(saved.bond)||0));
    saved.memories=Array.isArray(saved.memories)?saved.memories:[];
    return saved;
  }
  function lang(){return data.language==='es'?'es':'en';}
  function t(key){return copy[lang()][key]||copy.en[key]||key;}
  function el(id){return document.getElementById(id);}
  function setText(id,value){const node=el(id);if(node)node.textContent=value;}
  function safeDate(stamp){try{return new Intl.DateTimeFormat(lang()==='es'?'es-ES':'en-US',{day:'2-digit',month:'short'}).format(new Date(stamp));}catch(_){return '';}}
  function tamerSprite(look){
    const p=looks[look]||looks.sky;
    return '<svg viewBox="0 0 16 20" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges" aria-hidden="true"><rect x="5" y="2" width="6" height="2" fill="'+p.hair+'"/><rect x="4" y="4" width="8" height="5" fill="'+p.skin+'"/><rect x="3" y="3" width="2" height="4" fill="'+p.hair+'"/><rect x="11" y="3" width="2" height="4" fill="'+p.hair+'"/><rect x="6" y="6" width="1" height="1" fill="#172238"/><rect x="9" y="6" width="1" height="1" fill="#172238"/><rect x="7" y="9" width="2" height="1" fill="'+p.skin+'"/><rect x="7" y="10" width="2" height="2" fill="'+p.trim+'"/><rect x="5" y="11" width="6" height="4" fill="'+p.shirt+'"/><rect x="3" y="11" width="2" height="4" fill="'+p.skin+'"/><rect x="11" y="11" width="2" height="4" fill="'+p.skin+'"/><rect x="5" y="15" width="3" height="3" fill="#32415a"/><rect x="8" y="15" width="3" height="3" fill="#32415a"/><rect x="4" y="18" width="4" height="1" fill="#f3e3bc"/><rect x="8" y="18" width="4" height="1" fill="#f3e3bc"/></svg>';
  }
  function renderTamer(){
    const form=el('dgTamerForm'),summary=el('dgTamerSummary'),input=el('dgTamerName');
    if(!form||!summary)return;
    const ready=!!data.tamer,editing=data.editingTamer===true;
    form.hidden=ready&&!editing;summary.hidden=!ready||editing;
    if(input&&document.activeElement!==input)input.value=draftName;
    setText('dgTamerStatus',ready?t('tamerReady'):t('createTamerFirst'));
    const name=el('dgTamerSummaryName');if(name)name.textContent=data.tamer?.name||'';
    const art=el('dgTamerSummaryArt');if(art)art.innerHTML=tamerSprite(data.tamer?.look||'sky');
    document.querySelectorAll('[data-tamer-look]').forEach(button=>{
      const look=button.dataset.tamerLook,spot=button.querySelector('span');
      if(spot)spot.innerHTML=tamerSprite(look);
      button.classList.toggle('active',look===draftLook);
      button.setAttribute('aria-pressed',String(look===draftLook));
    });
  }
  function render(){
    const section=el('view-digiego'); if(!section)return;
    const l=lang(),partner=byId(data.selected),saved=partnerState(partner.id),unlocked=discovered();
    renderTamer();
    if(!unlocked.some(item=>item.id===partner.id)){data.selected='agumon';return render();}
    section.querySelectorAll('[data-dg]').forEach(node=>{const key=node.dataset.dg;if(key==='title')node.textContent=t('title');else if(key==='subtitle')node.textContent=t('subtitle');else if(key==='badge')node.textContent=t('badge');else if(copy[l][key])node.textContent=t(key);});
    const select=el('dgPartner');
    if(select){
      select.innerHTML=unlocked.map(item=>'<option value="'+item.id+'">'+item.name+' · '+item.stage+'</option>').join('');
      select.value=data.selected;
    }
    const art=el('dgPartnerArt');if(art){art.src=partner.asset||'assets/launcher/digimon/agumon.png';art.alt=partner.name;art.classList.toggle('dg-placeholder',!partner.asset);}
    setText('dgPartnerName',partner.name);setText('dgPartnerStage',partner.stage.toUpperCase());
    setText('dgTrait',partner.trait[l]);
    setText('dgQuip',partner.quip?.[l]||partner.trait[l]+'.');
    const hearts=Math.floor(saved.bond/20),full=Math.round(saved.bond/20);
    const heartRow=el('dgHearts');
    if(heartRow){heartRow.innerHTML=Array.from({length:5},(_,i)=>'<span class="dg-heart'+(i<hearts?' filled':i===hearts&&saved.bond%20?' partial':'')+'" aria-label="'+(i<hearts?'♥':'♡')+'">'+(i<hearts?'♥':'♡')+'</span>').join('');heartRow.setAttribute('aria-label',hearts+' / 5 '+t('hearts'));}
    const meter=el('dgBondFill');if(meter)meter.style.width=saved.bond+'%';
    setText('dgBondValue',hearts+' / 5 '+t('hearts'));
    setText('dgGiftNote',t('gift')+(saved.bond>=60?' '+t('giftLine'):''));
    setText('dgCarryNote',saved.bond>=100?t('carry'):'');
    const memories=el('dgMemories');
    if(memories){
      const items=saved.memories.slice(0,8);
      memories.innerHTML=(items.length?items.map(item=>'<article class="dg-memory"><small>'+safeDate(item.when)+' · '+(item.label||'DigiEgo')+'</small><p>'+escapeHtml(item.text)+'</p></article>').join(''):'<p class="dg-empty">'+t('empty')+'</p>');
    }
    setText('dgStatus',!data.tamer?t('createTamerFirst'):data.enabled?t('enabled'):t('disabled'));
    section.classList.toggle('dg-ego-off',!data.enabled);
    section.querySelectorAll('[data-dg-action]').forEach(button=>button.disabled=!data.enabled||!data.tamer);
    const partnerSelect=el('dgPartner');if(partnerSelect)partnerSelect.disabled=!data.tamer;
    const languageButtons=section.querySelectorAll('[data-dg-language]');
    languageButtons.forEach(button=>button.classList.toggle('active',button.dataset.dgLanguage===data.language));
    const off=el('dgOff');if(off){off.classList.toggle('active',!data.enabled);off.textContent=data.enabled?t('off'):t('on');}
    write(data);
  }
  function escapeHtml(value){return String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}
  function line(event,partner){
    const l=lang(),key=event+'Line';
    const intro={
      talk:l==='es'?'DigiEgo':'DigiEgo',
      praise:t('praise'),scold:t('scold'),pet:t('pet'),cold:t('cold'),race:t('race'),win:t('win'),farewell:t('farewell'),hint:t('hintLabel'),gift:t('gift')
    };
    const special=partner.voice&&partner.voice[event]&&partner.voice[event][l];
    if(special)return special;
    return t(key)||partner.quip?.[l]||intro[event]||partner.trait[l];
  }
  function remember(event,points){
    const partner=byId(data.selected),saved=partnerState(partner.id),l=lang();
    let text=line(event,partner);
    if(event==='start')text=copy[l].before+' '+(partner.quip?.[l]||partner.trait[l]);
    if(event==='hint')text=t('hinted');
    if(event==='gift')text=t('giftLine');
    const label=copy[l][event]||copy[l].sceneDone;
    saved.memories.unshift({event,label,text,when:Date.now()});
    saved.memories=saved.memories.slice(0,8);
    if(points){saved.bond=Math.max(0,Math.min(100,saved.bond+points));data.interactions++;}
    if(saved.bond>=60)saved.giftClaimed=true;
    if(saved.bond>=100)data.carryover=20;
    write(data);showDialogue(text);render();
    return text;
  }
  function showDialogue(text){
    const bubble=el('dgDialogue');if(!bubble)return;
    bubble.textContent=text;bubble.classList.remove('dg-pop');void bubble.offsetWidth;bubble.classList.add('dg-pop');
  }
  const actionPoints={talk:4,praise:5,scold:-2,pet:6,cold:10,race:12,win:12,farewell:8};
  document.addEventListener('submit',event=>{
    if(event.target.id==='dgTamerForm'){
      event.preventDefault();
      const input=el('dgTamerName'),name=(input?.value||'').trim().replace(/\s+/g,' ');
      if(name.length<2||name.length>16){input?.reportValidity();return;}
      draftName=name;
      data.tamer={name,look:looks[draftLook]?draftLook:'sky',createdAt:data.tamer?.createdAt||Date.now()};
      data.editingTamer=false;write(data);render();
      showDialogue(t('greet'));
    }
  });
  document.addEventListener('input',event=>{if(event.target.id==='dgTamerName')draftName=event.target.value;});
  document.addEventListener('click',event=>{
    const lookButton=event.target.closest('[data-tamer-look]');
    if(lookButton){draftLook=lookButton.dataset.tamerLook;renderTamer();return;}
    if(event.target.closest('#dgTamerEdit')){data.editingTamer=true;draftName=data.tamer?.name||'';draftLook=data.tamer?.look||'sky';renderTamer();return;}
    const langButton=event.target.closest('[data-dg-language]');
    if(langButton){data.language=langButton.dataset.dgLanguage;data.enabled=true;write(data);render();return;}
    if(event.target.closest('#dgOff')){data.enabled=!data.enabled;write(data);render();return;}
    const select=event.target.closest('#dgPartner');
    if(select){return;}
    const action=event.target.closest('[data-dg-action]');
    if(action&&!action.disabled){
      const type=action.dataset.dgAction;
      if(type==='talk'&&partnerState(data.selected).memories.length===0)remember('start',4);
      else remember(type,actionPoints[type]||0);
    }
  });
  document.addEventListener('change',event=>{
    if(event.target.id==='dgPartner'){
      const next=event.target.value;
      if(byId(next)){data.selected=next;partnerState(next);write(data);render();showDialogue(byId(next).quip?.[lang()]||byId(next).trait[lang()]);}
    }
  });
  document.addEventListener('storage',event=>{if(event.key===BUDDIES_KEY)render();});
  window.addEventListener('digirogue-buddy-update',render);
  window.addEventListener('hashchange',()=>{if(location.hash==='#digiego')render();});
  if(data.partners.agumon===undefined)partnerState('agumon').memories.unshift({event:'start',label:copy[lang()].life,text:copy[lang()].before,when:Date.now()});
  render();
})();
