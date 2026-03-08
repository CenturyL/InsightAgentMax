(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))n(t);new MutationObserver(t=>{for(const i of t)if(i.type==="childList")for(const a of i.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&n(a)}).observe(document,{childList:!0,subtree:!0});function s(t){const i={};return t.integrity&&(i.integrity=t.integrity),t.referrerPolicy&&(i.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?i.credentials="include":t.crossOrigin==="anonymous"?i.credentials="omit":i.credentials="same-origin",i}function n(t){if(t.ep)return;t.ep=!0;const i=s(t);fetch(t.href,i)}})();function Y(){return{async:!1,breaks:!1,extensions:null,gfm:!0,hooks:null,pedantic:!1,renderer:null,silent:!1,tokenizer:null,walkTokens:null}}var S=Y();function ve(r){S=r}var I={exec:()=>null};function d(r,e=""){let s=typeof r=="string"?r:r.source,n={replace:(t,i)=>{let a=typeof i=="string"?i:i.source;return a=a.replace(x.caret,"$1"),s=s.replace(t,a),n},getRegex:()=>new RegExp(s,e)};return n}var qe=(()=>{try{return!!new RegExp("(?<=1)(?<!1)")}catch{return!1}})(),x={codeRemoveIndent:/^(?: {1,4}| {0,3}\t)/gm,outputLinkReplace:/\\([\[\]])/g,indentCodeCompensation:/^(\s+)(?:```)/,beginningSpace:/^\s+/,endingHash:/#$/,startingSpaceChar:/^ /,endingSpaceChar:/ $/,nonSpaceChar:/[^ ]/,newLineCharGlobal:/\n/g,tabCharGlobal:/\t/g,multipleSpaceGlobal:/\s+/g,blankLine:/^[ \t]*$/,doubleBlankLine:/\n[ \t]*\n[ \t]*$/,blockquoteStart:/^ {0,3}>/,blockquoteSetextReplace:/\n {0,3}((?:=+|-+) *)(?=\n|$)/g,blockquoteSetextReplace2:/^ {0,3}>[ \t]?/gm,listReplaceTabs:/^\t+/,listReplaceNesting:/^ {1,4}(?=( {4})*[^ ])/g,listIsTask:/^\[[ xX]\] /,listReplaceTask:/^\[[ xX]\] +/,anyLine:/\n.*\n/,hrefBrackets:/^<(.*)>$/,tableDelimiter:/[:|]/,tableAlignChars:/^\||\| *$/g,tableRowBlankLine:/\n[ \t]*$/,tableAlignRight:/^ *-+: *$/,tableAlignCenter:/^ *:-+: *$/,tableAlignLeft:/^ *:-+ *$/,startATag:/^<a /i,endATag:/^<\/a>/i,startPreScriptTag:/^<(pre|code|kbd|script)(\s|>)/i,endPreScriptTag:/^<\/(pre|code|kbd|script)(\s|>)/i,startAngleBracket:/^</,endAngleBracket:/>$/,pedanticHrefTitle:/^([^'"]*[^\s])\s+(['"])(.*)\2/,unicodeAlphaNumeric:/[\p{L}\p{N}]/u,escapeTest:/[&<>"']/,escapeReplace:/[&<>"']/g,escapeTestNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/,escapeReplaceNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/g,unescapeTest:/&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig,caret:/(^|[^\[])\^/g,percentDecode:/%25/g,findPipe:/\|/g,splitPipe:/ \|/,slashPipe:/\\\|/g,carriageReturn:/\r\n|\r/g,spaceLine:/^ +$/gm,notSpaceStart:/^\S*/,endingNewline:/\n$/,listItemRegex:r=>new RegExp(`^( {0,3}${r})((?:[	 ][^\\n]*)?(?:\\n|$))`),nextBulletRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`),hrRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`),fencesBeginRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}(?:\`\`\`|~~~)`),headingBeginRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}#`),htmlBeginRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}<(?:[a-z].*>|!--)`,"i")},Me=/^(?:[ \t]*(?:\n|$))+/,Ne=/^((?: {4}| {0,3}\t)[^\n]+(?:\n(?:[ \t]*(?:\n|$))*)?)+/,Oe=/^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/,B=/^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/,De=/^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/,ee=/(?:[*+-]|\d{1,9}[.)])/,ye=/^(?!bull |blockCode|fences|blockquote|heading|html|table)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html|table))+?)\n {0,3}(=+|-+) *(?:\n+|$)/,$e=d(ye).replace(/bull/g,ee).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/\|table/g,"").getRegex(),He=d(ye).replace(/bull/g,ee).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/table/g,/ {0,3}\|?(?:[:\- ]*\|)+[\:\- ]*\n/).getRegex(),te=/^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/,Ze=/^[^\n]+/,re=/(?!\s*\])(?:\\[\s\S]|[^\[\]\\])+/,je=d(/^ {0,3}\[(label)\]: *(?:\n[ \t]*)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n[ \t]*)?| *\n[ \t]*)(title))? *(?:\n+|$)/).replace("label",re).replace("title",/(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(),Ke=d(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g,ee).getRegex(),Z="address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul",se=/<!--(?:-?>|[\s\S]*?(?:-->|$))/,Qe=d("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$))","i").replace("comment",se).replace("tag",Z).replace("attribute",/ +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(),Re=d(te).replace("hr",B).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("|table","").replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",Z).getRegex(),Fe=d(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph",Re).getRegex(),ne={blockquote:Fe,code:Ne,def:je,fences:Oe,heading:De,hr:B,html:Qe,lheading:$e,list:Ke,newline:Me,paragraph:Re,table:I,text:Ze},ge=d("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr",B).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("blockquote"," {0,3}>").replace("code","(?: {4}| {0,3}	)[^\\n]").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",Z).getRegex(),Ge={...ne,lheading:He,table:ge,paragraph:d(te).replace("hr",B).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("table",ge).replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",Z).getRegex()},Je={...ne,html:d(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment",se).replace(/tag/g,"(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),def:/^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,heading:/^(#{1,6})(.*)(?:\n+|$)/,fences:I,lheading:/^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,paragraph:d(te).replace("hr",B).replace("heading",` *#{1,6} *[^
]`).replace("lheading",$e).replace("|table","").replace("blockquote"," {0,3}>").replace("|fences","").replace("|list","").replace("|html","").replace("|tag","").getRegex()},Ue=/^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/,We=/^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/,Se=/^( {2,}|\\)\n(?!\s*$)/,Xe=/^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/,j=/[\p{P}\p{S}]/u,ae=/[\s\p{P}\p{S}]/u,Te=/[^\s\p{P}\p{S}]/u,Ve=d(/^((?![*_])punctSpace)/,"u").replace(/punctSpace/g,ae).getRegex(),_e=/(?!~)[\p{P}\p{S}]/u,Ye=/(?!~)[\s\p{P}\p{S}]/u,et=/(?:[^\s\p{P}\p{S}]|~)/u,tt=d(/link|precode-code|html/,"g").replace("link",/\[(?:[^\[\]`]|(?<a>`+)[^`]+\k<a>(?!`))*?\]\((?:\\[\s\S]|[^\\\(\)]|\((?:\\[\s\S]|[^\\\(\)])*\))*\)/).replace("precode-",qe?"(?<!`)()":"(^^|[^`])").replace("code",/(?<b>`+)[^`]+\k<b>(?!`)/).replace("html",/<(?! )[^<>]*?>/).getRegex(),Ce=/^(?:\*+(?:((?!\*)punct)|[^\s*]))|^_+(?:((?!_)punct)|([^\s_]))/,rt=d(Ce,"u").replace(/punct/g,j).getRegex(),st=d(Ce,"u").replace(/punct/g,_e).getRegex(),Ae="^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)punct(\\*+)(?=[\\s]|$)|notPunctSpace(\\*+)(?!\\*)(?=punctSpace|$)|(?!\\*)punctSpace(\\*+)(?=notPunctSpace)|[\\s](\\*+)(?!\\*)(?=punct)|(?!\\*)punct(\\*+)(?!\\*)(?=punct)|notPunctSpace(\\*+)(?=notPunctSpace)",nt=d(Ae,"gu").replace(/notPunctSpace/g,Te).replace(/punctSpace/g,ae).replace(/punct/g,j).getRegex(),at=d(Ae,"gu").replace(/notPunctSpace/g,et).replace(/punctSpace/g,Ye).replace(/punct/g,_e).getRegex(),it=d("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)punct(_+)(?=[\\s]|$)|notPunctSpace(_+)(?!_)(?=punctSpace|$)|(?!_)punctSpace(_+)(?=notPunctSpace)|[\\s](_+)(?!_)(?=punct)|(?!_)punct(_+)(?!_)(?=punct)","gu").replace(/notPunctSpace/g,Te).replace(/punctSpace/g,ae).replace(/punct/g,j).getRegex(),lt=d(/\\(punct)/,"gu").replace(/punct/g,j).getRegex(),ot=d(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme",/[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email",/[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(),ct=d(se).replace("(?:-->|$)","-->").getRegex(),pt=d("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment",ct).replace("attribute",/\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(),O=/(?:\[(?:\\[\s\S]|[^\[\]\\])*\]|\\[\s\S]|`+[^`]*?`+(?!`)|[^\[\]\\`])*?/,ht=d(/^!?\[(label)\]\(\s*(href)(?:(?:[ \t]*(?:\n[ \t]*)?)(title))?\s*\)/).replace("label",O).replace("href",/<(?:\\.|[^\n<>\\])+>|[^ \t\n\x00-\x1f]*/).replace("title",/"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(),Le=d(/^!?\[(label)\]\[(ref)\]/).replace("label",O).replace("ref",re).getRegex(),ze=d(/^!?\[(ref)\](?:\[\])?/).replace("ref",re).getRegex(),ut=d("reflink|nolink(?!\\()","g").replace("reflink",Le).replace("nolink",ze).getRegex(),ke=/[hH][tT][tT][pP][sS]?|[fF][tT][pP]/,ie={_backpedal:I,anyPunctuation:lt,autolink:ot,blockSkip:tt,br:Se,code:We,del:I,emStrongLDelim:rt,emStrongRDelimAst:nt,emStrongRDelimUnd:it,escape:Ue,link:ht,nolink:ze,punctuation:Ve,reflink:Le,reflinkSearch:ut,tag:pt,text:Xe,url:I},dt={...ie,link:d(/^!?\[(label)\]\((.*?)\)/).replace("label",O).getRegex(),reflink:d(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label",O).getRegex()},G={...ie,emStrongRDelimAst:at,emStrongLDelim:st,url:d(/^((?:protocol):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/).replace("protocol",ke).replace("email",/[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),_backpedal:/(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,del:/^(~~?)(?=[^\s~])((?:\\[\s\S]|[^\\])*?(?:\\[\s\S]|[^\s~\\]))\1(?=[^~]|$)/,text:d(/^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|protocol:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/).replace("protocol",ke).getRegex()},gt={...G,br:d(Se).replace("{2,}","*").getRegex(),text:d(G.text).replace("\\b_","\\b_| {2,}\\n").replace(/\{2,\}/g,"*").getRegex()},q={normal:ne,gfm:Ge,pedantic:Je},A={normal:ie,gfm:G,breaks:gt,pedantic:dt},kt={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"},fe=r=>kt[r];function $(r,e){if(e){if(x.escapeTest.test(r))return r.replace(x.escapeReplace,fe)}else if(x.escapeTestNoEncode.test(r))return r.replace(x.escapeReplaceNoEncode,fe);return r}function me(r){try{r=encodeURI(r).replace(x.percentDecode,"%")}catch{return null}return r}function be(r,e){let s=r.replace(x.findPipe,(i,a,o)=>{let l=!1,h=a;for(;--h>=0&&o[h]==="\\";)l=!l;return l?"|":" |"}),n=s.split(x.splitPipe),t=0;if(n[0].trim()||n.shift(),n.length>0&&!n.at(-1)?.trim()&&n.pop(),e)if(n.length>e)n.splice(e);else for(;n.length<e;)n.push("");for(;t<n.length;t++)n[t]=n[t].trim().replace(x.slashPipe,"|");return n}function L(r,e,s){let n=r.length;if(n===0)return"";let t=0;for(;t<n&&r.charAt(n-t-1)===e;)t++;return r.slice(0,n-t)}function ft(r,e){if(r.indexOf(e[1])===-1)return-1;let s=0;for(let n=0;n<r.length;n++)if(r[n]==="\\")n++;else if(r[n]===e[0])s++;else if(r[n]===e[1]&&(s--,s<0))return n;return s>0?-2:-1}function xe(r,e,s,n,t){let i=e.href,a=e.title||null,o=r[1].replace(t.other.outputLinkReplace,"$1");n.state.inLink=!0;let l={type:r[0].charAt(0)==="!"?"image":"link",raw:s,href:i,title:a,text:o,tokens:n.inlineTokens(o)};return n.state.inLink=!1,l}function mt(r,e,s){let n=r.match(s.other.indentCodeCompensation);if(n===null)return e;let t=n[1];return e.split(`
`).map(i=>{let a=i.match(s.other.beginningSpace);if(a===null)return i;let[o]=a;return o.length>=t.length?i.slice(t.length):i}).join(`
`)}var D=class{options;rules;lexer;constructor(r){this.options=r||S}space(r){let e=this.rules.block.newline.exec(r);if(e&&e[0].length>0)return{type:"space",raw:e[0]}}code(r){let e=this.rules.block.code.exec(r);if(e){let s=e[0].replace(this.rules.other.codeRemoveIndent,"");return{type:"code",raw:e[0],codeBlockStyle:"indented",text:this.options.pedantic?s:L(s,`
`)}}}fences(r){let e=this.rules.block.fences.exec(r);if(e){let s=e[0],n=mt(s,e[3]||"",this.rules);return{type:"code",raw:s,lang:e[2]?e[2].trim().replace(this.rules.inline.anyPunctuation,"$1"):e[2],text:n}}}heading(r){let e=this.rules.block.heading.exec(r);if(e){let s=e[2].trim();if(this.rules.other.endingHash.test(s)){let n=L(s,"#");(this.options.pedantic||!n||this.rules.other.endingSpaceChar.test(n))&&(s=n.trim())}return{type:"heading",raw:e[0],depth:e[1].length,text:s,tokens:this.lexer.inline(s)}}}hr(r){let e=this.rules.block.hr.exec(r);if(e)return{type:"hr",raw:L(e[0],`
`)}}blockquote(r){let e=this.rules.block.blockquote.exec(r);if(e){let s=L(e[0],`
`).split(`
`),n="",t="",i=[];for(;s.length>0;){let a=!1,o=[],l;for(l=0;l<s.length;l++)if(this.rules.other.blockquoteStart.test(s[l]))o.push(s[l]),a=!0;else if(!a)o.push(s[l]);else break;s=s.slice(l);let h=o.join(`
`),c=h.replace(this.rules.other.blockquoteSetextReplace,`
    $1`).replace(this.rules.other.blockquoteSetextReplace2,"");n=n?`${n}
${h}`:h,t=t?`${t}
${c}`:c;let f=this.lexer.state.top;if(this.lexer.state.top=!0,this.lexer.blockTokens(c,i,!0),this.lexer.state.top=f,s.length===0)break;let g=i.at(-1);if(g?.type==="code")break;if(g?.type==="blockquote"){let b=g,m=b.raw+`
`+s.join(`
`),w=this.blockquote(m);i[i.length-1]=w,n=n.substring(0,n.length-b.raw.length)+w.raw,t=t.substring(0,t.length-b.text.length)+w.text;break}else if(g?.type==="list"){let b=g,m=b.raw+`
`+s.join(`
`),w=this.list(m);i[i.length-1]=w,n=n.substring(0,n.length-g.raw.length)+w.raw,t=t.substring(0,t.length-b.raw.length)+w.raw,s=m.substring(i.at(-1).raw.length).split(`
`);continue}}return{type:"blockquote",raw:n,tokens:i,text:t}}}list(r){let e=this.rules.block.list.exec(r);if(e){let s=e[1].trim(),n=s.length>1,t={type:"list",raw:"",ordered:n,start:n?+s.slice(0,-1):"",loose:!1,items:[]};s=n?`\\d{1,9}\\${s.slice(-1)}`:`\\${s}`,this.options.pedantic&&(s=n?s:"[*+-]");let i=this.rules.other.listItemRegex(s),a=!1;for(;r;){let l=!1,h="",c="";if(!(e=i.exec(r))||this.rules.block.hr.test(r))break;h=e[0],r=r.substring(h.length);let f=e[2].split(`
`,1)[0].replace(this.rules.other.listReplaceTabs,K=>" ".repeat(3*K.length)),g=r.split(`
`,1)[0],b=!f.trim(),m=0;if(this.options.pedantic?(m=2,c=f.trimStart()):b?m=e[1].length+1:(m=e[2].search(this.rules.other.nonSpaceChar),m=m>4?1:m,c=f.slice(m),m+=e[1].length),b&&this.rules.other.blankLine.test(g)&&(h+=g+`
`,r=r.substring(g.length+1),l=!0),!l){let K=this.rules.other.nextBulletRegex(m),he=this.rules.other.hrRegex(m),ue=this.rules.other.fencesBeginRegex(m),de=this.rules.other.headingBeginRegex(m),Ee=this.rules.other.htmlBeginRegex(m);for(;r;){let Q=r.split(`
`,1)[0],C;if(g=Q,this.options.pedantic?(g=g.replace(this.rules.other.listReplaceNesting,"  "),C=g):C=g.replace(this.rules.other.tabCharGlobal,"    "),ue.test(g)||de.test(g)||Ee.test(g)||K.test(g)||he.test(g))break;if(C.search(this.rules.other.nonSpaceChar)>=m||!g.trim())c+=`
`+C.slice(m);else{if(b||f.replace(this.rules.other.tabCharGlobal,"    ").search(this.rules.other.nonSpaceChar)>=4||ue.test(f)||de.test(f)||he.test(f))break;c+=`
`+g}!b&&!g.trim()&&(b=!0),h+=Q+`
`,r=r.substring(Q.length+1),f=C.slice(m)}}t.loose||(a?t.loose=!0:this.rules.other.doubleBlankLine.test(h)&&(a=!0));let w=null,pe;this.options.gfm&&(w=this.rules.other.listIsTask.exec(c),w&&(pe=w[0]!=="[ ] ",c=c.replace(this.rules.other.listReplaceTask,""))),t.items.push({type:"list_item",raw:h,task:!!w,checked:pe,loose:!1,text:c,tokens:[]}),t.raw+=h}let o=t.items.at(-1);if(o)o.raw=o.raw.trimEnd(),o.text=o.text.trimEnd();else return;t.raw=t.raw.trimEnd();for(let l=0;l<t.items.length;l++)if(this.lexer.state.top=!1,t.items[l].tokens=this.lexer.blockTokens(t.items[l].text,[]),!t.loose){let h=t.items[l].tokens.filter(f=>f.type==="space"),c=h.length>0&&h.some(f=>this.rules.other.anyLine.test(f.raw));t.loose=c}if(t.loose)for(let l=0;l<t.items.length;l++)t.items[l].loose=!0;return t}}html(r){let e=this.rules.block.html.exec(r);if(e)return{type:"html",block:!0,raw:e[0],pre:e[1]==="pre"||e[1]==="script"||e[1]==="style",text:e[0]}}def(r){let e=this.rules.block.def.exec(r);if(e){let s=e[1].toLowerCase().replace(this.rules.other.multipleSpaceGlobal," "),n=e[2]?e[2].replace(this.rules.other.hrefBrackets,"$1").replace(this.rules.inline.anyPunctuation,"$1"):"",t=e[3]?e[3].substring(1,e[3].length-1).replace(this.rules.inline.anyPunctuation,"$1"):e[3];return{type:"def",tag:s,raw:e[0],href:n,title:t}}}table(r){let e=this.rules.block.table.exec(r);if(!e||!this.rules.other.tableDelimiter.test(e[2]))return;let s=be(e[1]),n=e[2].replace(this.rules.other.tableAlignChars,"").split("|"),t=e[3]?.trim()?e[3].replace(this.rules.other.tableRowBlankLine,"").split(`
`):[],i={type:"table",raw:e[0],header:[],align:[],rows:[]};if(s.length===n.length){for(let a of n)this.rules.other.tableAlignRight.test(a)?i.align.push("right"):this.rules.other.tableAlignCenter.test(a)?i.align.push("center"):this.rules.other.tableAlignLeft.test(a)?i.align.push("left"):i.align.push(null);for(let a=0;a<s.length;a++)i.header.push({text:s[a],tokens:this.lexer.inline(s[a]),header:!0,align:i.align[a]});for(let a of t)i.rows.push(be(a,i.header.length).map((o,l)=>({text:o,tokens:this.lexer.inline(o),header:!1,align:i.align[l]})));return i}}lheading(r){let e=this.rules.block.lheading.exec(r);if(e)return{type:"heading",raw:e[0],depth:e[2].charAt(0)==="="?1:2,text:e[1],tokens:this.lexer.inline(e[1])}}paragraph(r){let e=this.rules.block.paragraph.exec(r);if(e){let s=e[1].charAt(e[1].length-1)===`
`?e[1].slice(0,-1):e[1];return{type:"paragraph",raw:e[0],text:s,tokens:this.lexer.inline(s)}}}text(r){let e=this.rules.block.text.exec(r);if(e)return{type:"text",raw:e[0],text:e[0],tokens:this.lexer.inline(e[0])}}escape(r){let e=this.rules.inline.escape.exec(r);if(e)return{type:"escape",raw:e[0],text:e[1]}}tag(r){let e=this.rules.inline.tag.exec(r);if(e)return!this.lexer.state.inLink&&this.rules.other.startATag.test(e[0])?this.lexer.state.inLink=!0:this.lexer.state.inLink&&this.rules.other.endATag.test(e[0])&&(this.lexer.state.inLink=!1),!this.lexer.state.inRawBlock&&this.rules.other.startPreScriptTag.test(e[0])?this.lexer.state.inRawBlock=!0:this.lexer.state.inRawBlock&&this.rules.other.endPreScriptTag.test(e[0])&&(this.lexer.state.inRawBlock=!1),{type:"html",raw:e[0],inLink:this.lexer.state.inLink,inRawBlock:this.lexer.state.inRawBlock,block:!1,text:e[0]}}link(r){let e=this.rules.inline.link.exec(r);if(e){let s=e[2].trim();if(!this.options.pedantic&&this.rules.other.startAngleBracket.test(s)){if(!this.rules.other.endAngleBracket.test(s))return;let i=L(s.slice(0,-1),"\\");if((s.length-i.length)%2===0)return}else{let i=ft(e[2],"()");if(i===-2)return;if(i>-1){let a=(e[0].indexOf("!")===0?5:4)+e[1].length+i;e[2]=e[2].substring(0,i),e[0]=e[0].substring(0,a).trim(),e[3]=""}}let n=e[2],t="";if(this.options.pedantic){let i=this.rules.other.pedanticHrefTitle.exec(n);i&&(n=i[1],t=i[3])}else t=e[3]?e[3].slice(1,-1):"";return n=n.trim(),this.rules.other.startAngleBracket.test(n)&&(this.options.pedantic&&!this.rules.other.endAngleBracket.test(s)?n=n.slice(1):n=n.slice(1,-1)),xe(e,{href:n&&n.replace(this.rules.inline.anyPunctuation,"$1"),title:t&&t.replace(this.rules.inline.anyPunctuation,"$1")},e[0],this.lexer,this.rules)}}reflink(r,e){let s;if((s=this.rules.inline.reflink.exec(r))||(s=this.rules.inline.nolink.exec(r))){let n=(s[2]||s[1]).replace(this.rules.other.multipleSpaceGlobal," "),t=e[n.toLowerCase()];if(!t){let i=s[0].charAt(0);return{type:"text",raw:i,text:i}}return xe(s,t,s[0],this.lexer,this.rules)}}emStrong(r,e,s=""){let n=this.rules.inline.emStrongLDelim.exec(r);if(!(!n||n[3]&&s.match(this.rules.other.unicodeAlphaNumeric))&&(!(n[1]||n[2])||!s||this.rules.inline.punctuation.exec(s))){let t=[...n[0]].length-1,i,a,o=t,l=0,h=n[0][0]==="*"?this.rules.inline.emStrongRDelimAst:this.rules.inline.emStrongRDelimUnd;for(h.lastIndex=0,e=e.slice(-1*r.length+t);(n=h.exec(e))!=null;){if(i=n[1]||n[2]||n[3]||n[4]||n[5]||n[6],!i)continue;if(a=[...i].length,n[3]||n[4]){o+=a;continue}else if((n[5]||n[6])&&t%3&&!((t+a)%3)){l+=a;continue}if(o-=a,o>0)continue;a=Math.min(a,a+o+l);let c=[...n[0]][0].length,f=r.slice(0,t+n.index+c+a);if(Math.min(t,a)%2){let b=f.slice(1,-1);return{type:"em",raw:f,text:b,tokens:this.lexer.inlineTokens(b)}}let g=f.slice(2,-2);return{type:"strong",raw:f,text:g,tokens:this.lexer.inlineTokens(g)}}}}codespan(r){let e=this.rules.inline.code.exec(r);if(e){let s=e[2].replace(this.rules.other.newLineCharGlobal," "),n=this.rules.other.nonSpaceChar.test(s),t=this.rules.other.startingSpaceChar.test(s)&&this.rules.other.endingSpaceChar.test(s);return n&&t&&(s=s.substring(1,s.length-1)),{type:"codespan",raw:e[0],text:s}}}br(r){let e=this.rules.inline.br.exec(r);if(e)return{type:"br",raw:e[0]}}del(r){let e=this.rules.inline.del.exec(r);if(e)return{type:"del",raw:e[0],text:e[2],tokens:this.lexer.inlineTokens(e[2])}}autolink(r){let e=this.rules.inline.autolink.exec(r);if(e){let s,n;return e[2]==="@"?(s=e[1],n="mailto:"+s):(s=e[1],n=s),{type:"link",raw:e[0],text:s,href:n,tokens:[{type:"text",raw:s,text:s}]}}}url(r){let e;if(e=this.rules.inline.url.exec(r)){let s,n;if(e[2]==="@")s=e[0],n="mailto:"+s;else{let t;do t=e[0],e[0]=this.rules.inline._backpedal.exec(e[0])?.[0]??"";while(t!==e[0]);s=e[0],e[1]==="www."?n="http://"+e[0]:n=e[0]}return{type:"link",raw:e[0],text:s,href:n,tokens:[{type:"text",raw:s,text:s}]}}}inlineText(r){let e=this.rules.inline.text.exec(r);if(e){let s=this.lexer.state.inRawBlock;return{type:"text",raw:e[0],text:e[0],escaped:s}}}},v=class J{tokens;options;state;tokenizer;inlineQueue;constructor(e){this.tokens=[],this.tokens.links=Object.create(null),this.options=e||S,this.options.tokenizer=this.options.tokenizer||new D,this.tokenizer=this.options.tokenizer,this.tokenizer.options=this.options,this.tokenizer.lexer=this,this.inlineQueue=[],this.state={inLink:!1,inRawBlock:!1,top:!0};let s={other:x,block:q.normal,inline:A.normal};this.options.pedantic?(s.block=q.pedantic,s.inline=A.pedantic):this.options.gfm&&(s.block=q.gfm,this.options.breaks?s.inline=A.breaks:s.inline=A.gfm),this.tokenizer.rules=s}static get rules(){return{block:q,inline:A}}static lex(e,s){return new J(s).lex(e)}static lexInline(e,s){return new J(s).inlineTokens(e)}lex(e){e=e.replace(x.carriageReturn,`
`),this.blockTokens(e,this.tokens);for(let s=0;s<this.inlineQueue.length;s++){let n=this.inlineQueue[s];this.inlineTokens(n.src,n.tokens)}return this.inlineQueue=[],this.tokens}blockTokens(e,s=[],n=!1){for(this.options.pedantic&&(e=e.replace(x.tabCharGlobal,"    ").replace(x.spaceLine,""));e;){let t;if(this.options.extensions?.block?.some(a=>(t=a.call({lexer:this},e,s))?(e=e.substring(t.raw.length),s.push(t),!0):!1))continue;if(t=this.tokenizer.space(e)){e=e.substring(t.raw.length);let a=s.at(-1);t.raw.length===1&&a!==void 0?a.raw+=`
`:s.push(t);continue}if(t=this.tokenizer.code(e)){e=e.substring(t.raw.length);let a=s.at(-1);a?.type==="paragraph"||a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.text,this.inlineQueue.at(-1).src=a.text):s.push(t);continue}if(t=this.tokenizer.fences(e)){e=e.substring(t.raw.length),s.push(t);continue}if(t=this.tokenizer.heading(e)){e=e.substring(t.raw.length),s.push(t);continue}if(t=this.tokenizer.hr(e)){e=e.substring(t.raw.length),s.push(t);continue}if(t=this.tokenizer.blockquote(e)){e=e.substring(t.raw.length),s.push(t);continue}if(t=this.tokenizer.list(e)){e=e.substring(t.raw.length),s.push(t);continue}if(t=this.tokenizer.html(e)){e=e.substring(t.raw.length),s.push(t);continue}if(t=this.tokenizer.def(e)){e=e.substring(t.raw.length);let a=s.at(-1);a?.type==="paragraph"||a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.raw,this.inlineQueue.at(-1).src=a.text):this.tokens.links[t.tag]||(this.tokens.links[t.tag]={href:t.href,title:t.title},s.push(t));continue}if(t=this.tokenizer.table(e)){e=e.substring(t.raw.length),s.push(t);continue}if(t=this.tokenizer.lheading(e)){e=e.substring(t.raw.length),s.push(t);continue}let i=e;if(this.options.extensions?.startBlock){let a=1/0,o=e.slice(1),l;this.options.extensions.startBlock.forEach(h=>{l=h.call({lexer:this},o),typeof l=="number"&&l>=0&&(a=Math.min(a,l))}),a<1/0&&a>=0&&(i=e.substring(0,a+1))}if(this.state.top&&(t=this.tokenizer.paragraph(i))){let a=s.at(-1);n&&a?.type==="paragraph"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=a.text):s.push(t),n=i.length!==e.length,e=e.substring(t.raw.length);continue}if(t=this.tokenizer.text(e)){e=e.substring(t.raw.length);let a=s.at(-1);a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=a.text):s.push(t);continue}if(e){let a="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(a);break}else throw new Error(a)}}return this.state.top=!0,s}inline(e,s=[]){return this.inlineQueue.push({src:e,tokens:s}),s}inlineTokens(e,s=[]){let n=e,t=null;if(this.tokens.links){let l=Object.keys(this.tokens.links);if(l.length>0)for(;(t=this.tokenizer.rules.inline.reflinkSearch.exec(n))!=null;)l.includes(t[0].slice(t[0].lastIndexOf("[")+1,-1))&&(n=n.slice(0,t.index)+"["+"a".repeat(t[0].length-2)+"]"+n.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex))}for(;(t=this.tokenizer.rules.inline.anyPunctuation.exec(n))!=null;)n=n.slice(0,t.index)+"++"+n.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);let i;for(;(t=this.tokenizer.rules.inline.blockSkip.exec(n))!=null;)i=t[2]?t[2].length:0,n=n.slice(0,t.index+i)+"["+"a".repeat(t[0].length-i-2)+"]"+n.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);n=this.options.hooks?.emStrongMask?.call({lexer:this},n)??n;let a=!1,o="";for(;e;){a||(o=""),a=!1;let l;if(this.options.extensions?.inline?.some(c=>(l=c.call({lexer:this},e,s))?(e=e.substring(l.raw.length),s.push(l),!0):!1))continue;if(l=this.tokenizer.escape(e)){e=e.substring(l.raw.length),s.push(l);continue}if(l=this.tokenizer.tag(e)){e=e.substring(l.raw.length),s.push(l);continue}if(l=this.tokenizer.link(e)){e=e.substring(l.raw.length),s.push(l);continue}if(l=this.tokenizer.reflink(e,this.tokens.links)){e=e.substring(l.raw.length);let c=s.at(-1);l.type==="text"&&c?.type==="text"?(c.raw+=l.raw,c.text+=l.text):s.push(l);continue}if(l=this.tokenizer.emStrong(e,n,o)){e=e.substring(l.raw.length),s.push(l);continue}if(l=this.tokenizer.codespan(e)){e=e.substring(l.raw.length),s.push(l);continue}if(l=this.tokenizer.br(e)){e=e.substring(l.raw.length),s.push(l);continue}if(l=this.tokenizer.del(e)){e=e.substring(l.raw.length),s.push(l);continue}if(l=this.tokenizer.autolink(e)){e=e.substring(l.raw.length),s.push(l);continue}if(!this.state.inLink&&(l=this.tokenizer.url(e))){e=e.substring(l.raw.length),s.push(l);continue}let h=e;if(this.options.extensions?.startInline){let c=1/0,f=e.slice(1),g;this.options.extensions.startInline.forEach(b=>{g=b.call({lexer:this},f),typeof g=="number"&&g>=0&&(c=Math.min(c,g))}),c<1/0&&c>=0&&(h=e.substring(0,c+1))}if(l=this.tokenizer.inlineText(h)){e=e.substring(l.raw.length),l.raw.slice(-1)!=="_"&&(o=l.raw.slice(-1)),a=!0;let c=s.at(-1);c?.type==="text"?(c.raw+=l.raw,c.text+=l.text):s.push(l);continue}if(e){let c="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(c);break}else throw new Error(c)}}return s}},H=class{options;parser;constructor(r){this.options=r||S}space(r){return""}code({text:r,lang:e,escaped:s}){let n=(e||"").match(x.notSpaceStart)?.[0],t=r.replace(x.endingNewline,"")+`
`;return n?'<pre><code class="language-'+$(n)+'">'+(s?t:$(t,!0))+`</code></pre>
`:"<pre><code>"+(s?t:$(t,!0))+`</code></pre>
`}blockquote({tokens:r}){return`<blockquote>
${this.parser.parse(r)}</blockquote>
`}html({text:r}){return r}def(r){return""}heading({tokens:r,depth:e}){return`<h${e}>${this.parser.parseInline(r)}</h${e}>
`}hr(r){return`<hr>
`}list(r){let e=r.ordered,s=r.start,n="";for(let a=0;a<r.items.length;a++){let o=r.items[a];n+=this.listitem(o)}let t=e?"ol":"ul",i=e&&s!==1?' start="'+s+'"':"";return"<"+t+i+`>
`+n+"</"+t+`>
`}listitem(r){let e="";if(r.task){let s=this.checkbox({checked:!!r.checked});r.loose?r.tokens[0]?.type==="paragraph"?(r.tokens[0].text=s+" "+r.tokens[0].text,r.tokens[0].tokens&&r.tokens[0].tokens.length>0&&r.tokens[0].tokens[0].type==="text"&&(r.tokens[0].tokens[0].text=s+" "+$(r.tokens[0].tokens[0].text),r.tokens[0].tokens[0].escaped=!0)):r.tokens.unshift({type:"text",raw:s+" ",text:s+" ",escaped:!0}):e+=s+" "}return e+=this.parser.parse(r.tokens,!!r.loose),`<li>${e}</li>
`}checkbox({checked:r}){return"<input "+(r?'checked="" ':"")+'disabled="" type="checkbox">'}paragraph({tokens:r}){return`<p>${this.parser.parseInline(r)}</p>
`}table(r){let e="",s="";for(let t=0;t<r.header.length;t++)s+=this.tablecell(r.header[t]);e+=this.tablerow({text:s});let n="";for(let t=0;t<r.rows.length;t++){let i=r.rows[t];s="";for(let a=0;a<i.length;a++)s+=this.tablecell(i[a]);n+=this.tablerow({text:s})}return n&&(n=`<tbody>${n}</tbody>`),`<table>
<thead>
`+e+`</thead>
`+n+`</table>
`}tablerow({text:r}){return`<tr>
${r}</tr>
`}tablecell(r){let e=this.parser.parseInline(r.tokens),s=r.header?"th":"td";return(r.align?`<${s} align="${r.align}">`:`<${s}>`)+e+`</${s}>
`}strong({tokens:r}){return`<strong>${this.parser.parseInline(r)}</strong>`}em({tokens:r}){return`<em>${this.parser.parseInline(r)}</em>`}codespan({text:r}){return`<code>${$(r,!0)}</code>`}br(r){return"<br>"}del({tokens:r}){return`<del>${this.parser.parseInline(r)}</del>`}link({href:r,title:e,tokens:s}){let n=this.parser.parseInline(s),t=me(r);if(t===null)return n;r=t;let i='<a href="'+r+'"';return e&&(i+=' title="'+$(e)+'"'),i+=">"+n+"</a>",i}image({href:r,title:e,text:s,tokens:n}){n&&(s=this.parser.parseInline(n,this.parser.textRenderer));let t=me(r);if(t===null)return $(s);r=t;let i=`<img src="${r}" alt="${s}"`;return e&&(i+=` title="${$(e)}"`),i+=">",i}text(r){return"tokens"in r&&r.tokens?this.parser.parseInline(r.tokens):"escaped"in r&&r.escaped?r.text:$(r.text)}},le=class{strong({text:e}){return e}em({text:e}){return e}codespan({text:e}){return e}del({text:e}){return e}html({text:e}){return e}text({text:e}){return e}link({text:e}){return""+e}image({text:e}){return""+e}br(){return""}},y=class U{options;renderer;textRenderer;constructor(e){this.options=e||S,this.options.renderer=this.options.renderer||new H,this.renderer=this.options.renderer,this.renderer.options=this.options,this.renderer.parser=this,this.textRenderer=new le}static parse(e,s){return new U(s).parse(e)}static parseInline(e,s){return new U(s).parseInline(e)}parse(e,s=!0){let n="";for(let t=0;t<e.length;t++){let i=e[t];if(this.options.extensions?.renderers?.[i.type]){let o=i,l=this.options.extensions.renderers[o.type].call({parser:this},o);if(l!==!1||!["space","hr","heading","code","table","blockquote","list","html","def","paragraph","text"].includes(o.type)){n+=l||"";continue}}let a=i;switch(a.type){case"space":{n+=this.renderer.space(a);continue}case"hr":{n+=this.renderer.hr(a);continue}case"heading":{n+=this.renderer.heading(a);continue}case"code":{n+=this.renderer.code(a);continue}case"table":{n+=this.renderer.table(a);continue}case"blockquote":{n+=this.renderer.blockquote(a);continue}case"list":{n+=this.renderer.list(a);continue}case"html":{n+=this.renderer.html(a);continue}case"def":{n+=this.renderer.def(a);continue}case"paragraph":{n+=this.renderer.paragraph(a);continue}case"text":{let o=a,l=this.renderer.text(o);for(;t+1<e.length&&e[t+1].type==="text";)o=e[++t],l+=`
`+this.renderer.text(o);s?n+=this.renderer.paragraph({type:"paragraph",raw:l,text:l,tokens:[{type:"text",raw:l,text:l,escaped:!0}]}):n+=l;continue}default:{let o='Token with "'+a.type+'" type was not found.';if(this.options.silent)return console.error(o),"";throw new Error(o)}}}return n}parseInline(e,s=this.renderer){let n="";for(let t=0;t<e.length;t++){let i=e[t];if(this.options.extensions?.renderers?.[i.type]){let o=this.options.extensions.renderers[i.type].call({parser:this},i);if(o!==!1||!["escape","html","link","image","strong","em","codespan","br","del","text"].includes(i.type)){n+=o||"";continue}}let a=i;switch(a.type){case"escape":{n+=s.text(a);break}case"html":{n+=s.html(a);break}case"link":{n+=s.link(a);break}case"image":{n+=s.image(a);break}case"strong":{n+=s.strong(a);break}case"em":{n+=s.em(a);break}case"codespan":{n+=s.codespan(a);break}case"br":{n+=s.br(a);break}case"del":{n+=s.del(a);break}case"text":{n+=s.text(a);break}default:{let o='Token with "'+a.type+'" type was not found.';if(this.options.silent)return console.error(o),"";throw new Error(o)}}}return n}},z=class{options;block;constructor(r){this.options=r||S}static passThroughHooks=new Set(["preprocess","postprocess","processAllTokens","emStrongMask"]);static passThroughHooksRespectAsync=new Set(["preprocess","postprocess","processAllTokens"]);preprocess(r){return r}postprocess(r){return r}processAllTokens(r){return r}emStrongMask(r){return r}provideLexer(){return this.block?v.lex:v.lexInline}provideParser(){return this.block?y.parse:y.parseInline}},bt=class{defaults=Y();options=this.setOptions;parse=this.parseMarkdown(!0);parseInline=this.parseMarkdown(!1);Parser=y;Renderer=H;TextRenderer=le;Lexer=v;Tokenizer=D;Hooks=z;constructor(...r){this.use(...r)}walkTokens(r,e){let s=[];for(let n of r)switch(s=s.concat(e.call(this,n)),n.type){case"table":{let t=n;for(let i of t.header)s=s.concat(this.walkTokens(i.tokens,e));for(let i of t.rows)for(let a of i)s=s.concat(this.walkTokens(a.tokens,e));break}case"list":{let t=n;s=s.concat(this.walkTokens(t.items,e));break}default:{let t=n;this.defaults.extensions?.childTokens?.[t.type]?this.defaults.extensions.childTokens[t.type].forEach(i=>{let a=t[i].flat(1/0);s=s.concat(this.walkTokens(a,e))}):t.tokens&&(s=s.concat(this.walkTokens(t.tokens,e)))}}return s}use(...r){let e=this.defaults.extensions||{renderers:{},childTokens:{}};return r.forEach(s=>{let n={...s};if(n.async=this.defaults.async||n.async||!1,s.extensions&&(s.extensions.forEach(t=>{if(!t.name)throw new Error("extension name required");if("renderer"in t){let i=e.renderers[t.name];i?e.renderers[t.name]=function(...a){let o=t.renderer.apply(this,a);return o===!1&&(o=i.apply(this,a)),o}:e.renderers[t.name]=t.renderer}if("tokenizer"in t){if(!t.level||t.level!=="block"&&t.level!=="inline")throw new Error("extension level must be 'block' or 'inline'");let i=e[t.level];i?i.unshift(t.tokenizer):e[t.level]=[t.tokenizer],t.start&&(t.level==="block"?e.startBlock?e.startBlock.push(t.start):e.startBlock=[t.start]:t.level==="inline"&&(e.startInline?e.startInline.push(t.start):e.startInline=[t.start]))}"childTokens"in t&&t.childTokens&&(e.childTokens[t.name]=t.childTokens)}),n.extensions=e),s.renderer){let t=this.defaults.renderer||new H(this.defaults);for(let i in s.renderer){if(!(i in t))throw new Error(`renderer '${i}' does not exist`);if(["options","parser"].includes(i))continue;let a=i,o=s.renderer[a],l=t[a];t[a]=(...h)=>{let c=o.apply(t,h);return c===!1&&(c=l.apply(t,h)),c||""}}n.renderer=t}if(s.tokenizer){let t=this.defaults.tokenizer||new D(this.defaults);for(let i in s.tokenizer){if(!(i in t))throw new Error(`tokenizer '${i}' does not exist`);if(["options","rules","lexer"].includes(i))continue;let a=i,o=s.tokenizer[a],l=t[a];t[a]=(...h)=>{let c=o.apply(t,h);return c===!1&&(c=l.apply(t,h)),c}}n.tokenizer=t}if(s.hooks){let t=this.defaults.hooks||new z;for(let i in s.hooks){if(!(i in t))throw new Error(`hook '${i}' does not exist`);if(["options","block"].includes(i))continue;let a=i,o=s.hooks[a],l=t[a];z.passThroughHooks.has(i)?t[a]=h=>{if(this.defaults.async&&z.passThroughHooksRespectAsync.has(i))return(async()=>{let f=await o.call(t,h);return l.call(t,f)})();let c=o.call(t,h);return l.call(t,c)}:t[a]=(...h)=>{if(this.defaults.async)return(async()=>{let f=await o.apply(t,h);return f===!1&&(f=await l.apply(t,h)),f})();let c=o.apply(t,h);return c===!1&&(c=l.apply(t,h)),c}}n.hooks=t}if(s.walkTokens){let t=this.defaults.walkTokens,i=s.walkTokens;n.walkTokens=function(a){let o=[];return o.push(i.call(this,a)),t&&(o=o.concat(t.call(this,a))),o}}this.defaults={...this.defaults,...n}}),this}setOptions(r){return this.defaults={...this.defaults,...r},this}lexer(r,e){return v.lex(r,e??this.defaults)}parser(r,e){return y.parse(r,e??this.defaults)}parseMarkdown(r){return(e,s)=>{let n={...s},t={...this.defaults,...n},i=this.onError(!!t.silent,!!t.async);if(this.defaults.async===!0&&n.async===!1)return i(new Error("marked(): The async option was set to true by an extension. Remove async: false from the parse options object to return a Promise."));if(typeof e>"u"||e===null)return i(new Error("marked(): input parameter is undefined or null"));if(typeof e!="string")return i(new Error("marked(): input parameter is of type "+Object.prototype.toString.call(e)+", string expected"));if(t.hooks&&(t.hooks.options=t,t.hooks.block=r),t.async)return(async()=>{let a=t.hooks?await t.hooks.preprocess(e):e,o=await(t.hooks?await t.hooks.provideLexer():r?v.lex:v.lexInline)(a,t),l=t.hooks?await t.hooks.processAllTokens(o):o;t.walkTokens&&await Promise.all(this.walkTokens(l,t.walkTokens));let h=await(t.hooks?await t.hooks.provideParser():r?y.parse:y.parseInline)(l,t);return t.hooks?await t.hooks.postprocess(h):h})().catch(i);try{t.hooks&&(e=t.hooks.preprocess(e));let a=(t.hooks?t.hooks.provideLexer():r?v.lex:v.lexInline)(e,t);t.hooks&&(a=t.hooks.processAllTokens(a)),t.walkTokens&&this.walkTokens(a,t.walkTokens);let o=(t.hooks?t.hooks.provideParser():r?y.parse:y.parseInline)(a,t);return t.hooks&&(o=t.hooks.postprocess(o)),o}catch(a){return i(a)}}}onError(r,e){return s=>{if(s.message+=`
Please report this to https://github.com/markedjs/marked.`,r){let n="<p>An error occurred:</p><pre>"+$(s.message+"",!0)+"</pre>";return e?Promise.resolve(n):n}if(e)return Promise.reject(s);throw s}}},R=new bt;function k(r,e){return R.parse(r,e)}k.options=k.setOptions=function(r){return R.setOptions(r),k.defaults=R.defaults,ve(k.defaults),k};k.getDefaults=Y;k.defaults=S;k.use=function(...r){return R.use(...r),k.defaults=R.defaults,ve(k.defaults),k};k.walkTokens=function(r,e){return R.walkTokens(r,e)};k.parseInline=R.parseInline;k.Parser=y;k.parser=y.parse;k.Renderer=H;k.TextRenderer=le;k.Lexer=v;k.lexer=v.lex;k.Tokenizer=D;k.Hooks=z;k.parse=k;k.options;k.setOptions;k.use;k.walkTokens;k.parseInline;y.parse;v.lex;function Ie(){if(globalThis.crypto?.randomUUID)return globalThis.crypto.randomUUID();const r=Math.random().toString(36).slice(2,10);return`thread-${Date.now()}-${r}`}const xt=Ie(),u={apiBase:localStorage.getItem("agent-api-base")||"/api/v1",threadId:localStorage.getItem("agent-thread-id")||xt,messages:[],latestRetrievalMetrics:null,latestCompareReport:null,latestBenchmarkMetrics:null,activeTrace:[],statusTimer:null,requestStartedAt:null,activeQuestion:""};k.setOptions({gfm:!0,breaks:!0});const wt=document.querySelector("#app");wt.innerHTML=`
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark">IA</div>
        <div>
          <p class="eyebrow">Policy And Tender Agent</p>
          <h1>InsightAgent</h1>
        </div>
      </div>

      <div class="stack">
        <label class="field">
          <span>API Base</span>
          <input id="apiBase" value="${u.apiBase}" placeholder="/api/v1" />
        </label>
        <label class="field">
          <span>Thread ID</span>
          <div class="inline">
            <input id="threadId" value="${u.threadId}" />
            <button id="regenThread" class="ghost">重置</button>
          </div>
        </label>
        <label class="field">
          <span>User ID</span>
          <input id="userId" placeholder="例如：liushiji" />
        </label>
      </div>

      <div class="mini-metrics compact-metrics">
        <div class="mini-card">
          <span>Chat Mode</span>
          <strong>ReAct + Planner</strong>
        </div>
        <div class="mini-card">
          <span>Retrieval</span>
          <strong>Hybrid + Rerank</strong>
        </div>
        <div class="mini-card">
          <span>Ops</span>
          <strong>Eval + Benchmark</strong>
        </div>
      </div>

      <section class="panel compact-panel">
        <div class="panel-head tight">
          <div>
            <p class="eyebrow">Testing</p>
            <h3>测试环境重建</h3>
          </div>
        </div>
        <div class="compact-actions">
          <label class="check">
            <input id="forceDownload" type="checkbox" />
            <span>强制下载</span>
          </label>
          <label class="check">
            <input id="runRetrievalEvalAfterRebuild" type="checkbox" checked />
            <span>自动评估</span>
          </label>
        </div>
        <button id="rebuildEnv">重建环境</button>
        <pre id="rebuildResult" class="result-box compact-result"></pre>
      </section>

      <section class="panel compact-panel">
        <div class="panel-head tight">
          <div>
            <p class="eyebrow">Knowledge</p>
            <h3>知识库上传</h3>
          </div>
        </div>
        <div class="stack">
          <input id="knowledgeFile" type="file" />
          <button id="uploadKnowledge">上传并入库</button>
          <pre id="uploadResult" class="result-box compact-result"></pre>
        </div>
      </section>
    </aside>

    <main class="workspace">
      <header class="workspace-header">
        <div>
          <p class="eyebrow">Agent Console</p>
          <h2>InsightAgent</h2>
          <p class="hero-text">面向政策通知、招投标公告与本地知识资料分析的多模式 Agent 工作台。</p>
        </div>
        <div class="hero-metrics" id="summaryCards"></div>
      </header>

      <section class="panel chat-panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Chat</p>
            <h3>对话工作区</h3>
          </div>
          <div class="inline compact">
            <label class="field slim">
              <span>Task Mode</span>
              <select id="taskMode">
                <option value="">auto</option>
                <option value="qa">qa</option>
                <option value="compare">compare</option>
                <option value="extract">extract</option>
                <option value="report">report</option>
              </select>
            </label>
            <button id="clearChat" class="ghost">清空会话</button>
          </div>
        </div>

        <div class="workbench-grid">
          <section class="response-card primary-card message-column">
            <div class="message-head">
              <p class="eyebrow">Conversation</p>
              <strong>聊天记录</strong>
            </div>
            <div id="messageList" class="message-list"></div>
          </section>

          <section class="response-card primary-card">
            <div class="response-head">
              <p class="eyebrow">Answer</p>
              <strong>当前回答</strong>
            </div>
            <div id="answerPreview" class="answer-preview markdown-body">等待发送请求...</div>
          </section>

          <section class="response-card secondary-card">
            <div class="response-head">
              <p class="eyebrow">Trace</p>
              <strong>执行过程</strong>
            </div>
            <div id="traceList" class="trace-list">
              <div class="empty-chat">发送一条消息后，这里会显示路由、规划、检索等过程。</div>
            </div>
          </section>

          <section class="response-card secondary-card composer-card">
            <div class="response-head">
              <p class="eyebrow">Prompt</p>
              <strong>提问</strong>
            </div>
            <textarea id="query" placeholder="输入问题，例如：请比较上海浦东新区两份政策通知在支持对象和支持方向上的差异，并整理成要点。"></textarea>
            <label class="field slim grow">
              <span>Metadata Filters (JSON)</span>
              <input id="metadataFilters" placeholder='{"doc_category":"policy","region":"上海"}' />
            </label>
            <div class="live-status" id="agentStatus">等待发送请求...</div>
            <div class="composer-actions">
              <button id="sendChat">发送</button>
            </div>
          </section>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Evaluation</p>
            <h3>评估与 Benchmark</h3>
          </div>
          <div class="inline compact">
            <label class="field slim">
              <span>Top K</span>
              <input id="topK" type="number" min="1" max="20" value="3" />
            </label>
            <label class="field slim">
              <span>Candidate K</span>
              <input id="candidateK" type="number" min="1" max="100" value="12" />
            </label>
            <label class="field slim">
              <span>Strategy</span>
              <select id="strategy">
                <option value="hybrid_rerank">hybrid_rerank</option>
                <option value="dense_only">dense_only</option>
                <option value="dense_rerank">dense_rerank</option>
                <option value="hybrid_only">hybrid_only</option>
              </select>
            </label>
          </div>
        </div>

        <div class="inline wrap">
          <button id="runRetrievalEval">Retrieval Eval</button>
          <button id="runCompare" class="ghost">Baseline Compare</button>
          <button id="runGenerationEval" class="ghost">Generation Eval</button>
          <button id="runBenchmark" class="ghost">System Benchmark</button>
        </div>

        <div class="dashboard-grid">
          <section class="dashboard-card">
            <div class="chart-head">
              <div>
                <p class="eyebrow">Metrics</p>
                <h4>关键指标卡片</h4>
              </div>
            </div>
            <div id="metricCards" class="metric-grid"></div>
          </section>

          <section class="dashboard-card">
            <div class="chart-head">
              <div>
                <p class="eyebrow">Compare</p>
                <h4>Baseline 柱状图</h4>
              </div>
            </div>
            <div id="compareChart" class="chart-panel empty-state">运行 Baseline Compare 后显示</div>
          </section>

          <section class="dashboard-card span-2">
            <div class="chart-head">
              <div>
                <p class="eyebrow">Latency</p>
                <h4>Benchmark 图表</h4>
              </div>
            </div>
            <div id="benchmarkChart" class="chart-panel empty-state">运行 System Benchmark 后显示</div>
          </section>
        </div>

        <pre id="evalResult" class="result-box large"></pre>
      </section>
    </main>
  </div>
`;const p=r=>document.querySelector(r),we=p("#apiBase"),W=p("#threadId");function T(r,e=4){return r==null||Number.isNaN(Number(r))?"-":Number(r).toFixed(e)}function vt(r){const e=r.trim();return e?JSON.parse(e):null}function _(r,e){r.textContent=typeof e=="string"?e:JSON.stringify(e,null,2)}function F(r,e){u.messages.push({role:r,content:e,time:new Date().toLocaleTimeString("zh-CN",{hour12:!1})}),oe()}function oe(){const r=p("#messageList");if(!u.messages.length){r.innerHTML='<div class="empty-chat">发送一条消息后，聊天记录会显示在这里。</div>';return}r.innerHTML=u.messages.map(e=>`
        <article class="message-card ${e.role}">
          <header>
            <strong>${e.role==="user"?"User":"Agent"}</strong>
            <span>${e.time}</span>
          </header>
          <div class="message-body ${e.role==="agent"?"markdown-body":""}">${e.role==="agent"?k.parse(e.content||""):ce(e.content).replace(/\n/g,"<br/>")}</div>
        </article>
      `).join("")}function ce(r){return r.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}function yt(r){const e=r.trim();return e?/^(🧭|🛠️|✅|🔍|📎|💡|⚙️|🚦|📌|🔀|🧠|\[[^\]]+\])/.test(e):!1}function Be(r){const e=r.split(`
`),s=[],n=[];for(const t of e){if(yt(t)){s.push(t.trim());continue}n.push(t)}return{trace:s,answer:n.join(`
`).trim()}}function X(r){const e=p("#traceList");if(!r.length){e.innerHTML='<div class="empty-chat">等待后端返回执行过程...</div>';return}e.innerHTML=r.map((s,n)=>`
        <div class="trace-item">
          <span class="trace-step">${n+1}</span>
          <div>${ce(s)}</div>
        </div>
      `).join("")}function M(r){const e=p("#answerPreview"),s=u.activeQuestion?`<section class="answer-question"><span>本轮问题</span><strong>${ce(u.activeQuestion)}</strong></section>`:"";if(!r){e.innerHTML=`
      ${s}
      <div class="empty-chat">正在等待模型生成正文...</div>
    `;return}e.innerHTML=`
    ${s}
    <section class="answer-body">${k.parse(r)}</section>
  `}function V(){u.statusTimer&&(clearInterval(u.statusTimer),u.statusTimer=null)}function $t(){V(),u.requestStartedAt=Date.now();const r=p("#agentStatus");r.textContent="Agent 正在接收请求...",u.statusTimer=setInterval(()=>{const e=Math.round((Date.now()-u.requestStartedAt)/1e3),s=u.activeTrace[u.activeTrace.length-1];s?r.textContent=`${s} · ${e}s`:r.textContent=`Agent 正在规划 / 检索 / 生成... · ${e}s`},400)}function Rt(){const r=p("#summaryCards"),e=u.latestRetrievalMetrics,s=u.latestBenchmarkMetrics,n=[{label:"最近 Recall@K",value:e?T(e.avg_recall_at_k,4):"待运行",tone:"warm"},{label:"最近 MRR",value:e?T(e.mrr,4):"待运行",tone:"teal"},{label:"复杂任务时延",value:s?`${T(s.complex_request_latency_ms,2)} ms`:"待运行",tone:"dark"}];r.innerHTML=n.map(t=>`
        <div class="metric metric-${t.tone}">
          <span>${t.label}</span>
          <strong>${t.value}</strong>
        </div>
      `).join("")}function St(){const r=p("#metricCards"),e=u.latestRetrievalMetrics,s=u.latestBenchmarkMetrics,n=[["Precision@K",e?.avg_precision_at_k,4],["Recall@K",e?.avg_recall_at_k,4],["MRR",e?.mrr,4],["nDCG@K",e?.ndcg_at_k,4],["Avg Query Latency",e?`${T(e.avg_query_latency_ms,2)} ms`:null,null],["Complex Latency",s?`${T(s.complex_request_latency_ms,2)} ms`:null,null]];r.innerHTML=n.map(([t,i,a])=>{const o=typeof i=="string"?i:i==null?"待运行":T(i,a||4);return`
        <div class="stat-card">
          <span>${t}</span>
          <strong>${o}</strong>
        </div>
      `}).join("")}function N(r,e,s,n="",t=4){const i=s>0?Math.max(e/s*100,4):0,a=typeof e=="number"?`${e.toFixed(t)}${n}`:e;return`
    <div class="bar-row">
      <div class="bar-meta">
        <strong>${r}</strong>
        <span>${a}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${i}%"></div>
      </div>
    </div>
  `}function Tt(){const r=p("#compareChart"),e=u.latestCompareReport;if(!e?.baselines?.length){r.className="chart-panel empty-state",r.textContent="运行 Baseline Compare 后显示";return}const s=Math.max(...e.baselines.map(i=>i.avg_recall_at_k),1),n=Math.max(...e.baselines.map(i=>i.mrr),1),t=Math.max(...e.baselines.map(i=>i.avg_query_latency_ms),1);r.className="chart-panel",r.innerHTML=e.baselines.map(i=>`
        <section class="compare-card">
          <h5>${i.strategy}</h5>
          ${N("Recall",i.avg_recall_at_k,s)}
          ${N("MRR",i.mrr,n)}
          ${N("Latency",i.avg_query_latency_ms,t," ms",2)}
        </section>
      `).join("")}function _t(){const r=p("#benchmarkChart"),e=u.latestBenchmarkMetrics;if(!e){r.className="chart-panel empty-state",r.textContent="运行 System Benchmark 后显示";return}const s=[["Retrieval Avg",e.retrieval_avg_latency_ms],["Retrieval P95",e.retrieval_p95_latency_ms],["Simple Request",e.simple_request_latency_ms],["Complex Request",e.complex_request_latency_ms]],n=Math.max(...s.map(([,t])=>t),1);r.className="chart-panel benchmark-layout",r.innerHTML=s.map(([t,i])=>N(t,i,n," ms",2)).join("")}function P(){Rt(),St(),Tt(),_t()}async function Ct(r,e){if(!r.body)throw new Error("stream body not available");const s=r.body.getReader(),n=new TextDecoder("utf-8");let t="";for(;;){const{done:i,value:a}=await s.read();if(i)break;t+=n.decode(a,{stream:!0}),e.textContent=t,e.scrollTop=e.scrollHeight;const o=Be(t);u.activeTrace=o.trace,X(o.trace),M(o.answer)}return t}async function E(r,e={}){const s=await fetch(`${u.apiBase}${r}`,{headers:{"Content-Type":"application/json",...e.headers||{}},...e});if(!s.ok){const n=await s.text();throw new Error(n||`request failed: ${s.status}`)}return s.json()}we.addEventListener("change",()=>{u.apiBase=we.value.trim()||"/api/v1",localStorage.setItem("agent-api-base",u.apiBase)});W.addEventListener("change",()=>{u.threadId=W.value.trim(),localStorage.setItem("agent-thread-id",u.threadId)});p("#regenThread").addEventListener("click",()=>{u.threadId=Ie(),W.value=u.threadId,localStorage.setItem("agent-thread-id",u.threadId)});p("#clearChat").addEventListener("click",()=>{u.messages=[],u.activeQuestion="",p("#answerPreview").innerHTML='<div class="empty-chat">会话已清空。</div>',p("#traceList").innerHTML='<div class="empty-chat">会话已清空。</div>',p("#agentStatus").textContent="会话已清空。",oe()});async function Pe(){const r=p("#query"),e=r.value.trim();if(!e){p("#agentStatus").textContent="请输入问题。";return}u.activeQuestion=e,u.activeTrace=[],X([]),M(""),$t(),F("user",e),r.value="";try{const s=vt(p("#metadataFilters").value),n=await fetch(`${u.apiBase}/chat/agent`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,thread_id:u.threadId,user_id:p("#userId").value.trim(),task_mode:p("#taskMode").value||null,metadata_filters:s})});if(!n.ok)throw new Error(await n.text());const t=document.createElement("pre"),i=await Ct(n,t),a=Be(i);X(a.trace),M(a.answer),p("#agentStatus").textContent="生成完成",F("agent",a.answer||i||"空响应"),V()}catch(s){V(),p("#agentStatus").textContent=`请求失败：${s.message}`,M(`请求失败：${s.message}`),F("agent",`请求失败：${s.message}`)}}p("#sendChat").addEventListener("click",Pe);p("#query").addEventListener("keydown",r=>{r.key==="Enter"&&!r.shiftKey&&(r.preventDefault(),Pe())});p("#uploadKnowledge").addEventListener("click",async()=>{const r=p("#knowledgeFile").files[0],e=p("#uploadResult");if(!r){e.textContent="请先选择文件。";return}try{const s=new FormData;s.append("file",r);const t=await(await fetch(`${u.apiBase}/knowledge/upload`,{method:"POST",body:s})).json();_(e,t)}catch(s){e.textContent=`上传失败：${s.message}`}});p("#rebuildEnv").addEventListener("click",async()=>{const r=p("#rebuildResult");r.textContent="正在重建测试环境...";try{const e=await E("/testing/rebuild",{method:"POST",body:JSON.stringify({force_download:p("#forceDownload").checked,run_retrieval_eval:p("#runRetrievalEvalAfterRebuild").checked})});_(r,e),e?.result?.retrieval_eval&&(u.latestRetrievalMetrics=e.result.retrieval_eval,P())}catch(e){r.textContent=`重建失败：${e.message}`}});p("#runRetrievalEval").addEventListener("click",async()=>{const r=p("#evalResult");r.textContent="正在运行 retrieval eval...";try{const e=await E("/eval/retrieval",{method:"POST",body:JSON.stringify({top_k:Number(p("#topK").value),candidate_k:Number(p("#candidateK").value),strategy:p("#strategy").value})});_(r,e),u.latestRetrievalMetrics=e.metrics,P()}catch(e){r.textContent=`retrieval eval 失败：${e.message}`}});p("#runCompare").addEventListener("click",async()=>{const r=p("#evalResult");r.textContent="正在运行 baseline compare...";try{const e=await E("/eval/retrieval/compare",{method:"POST",body:JSON.stringify({top_k:Number(p("#topK").value),candidate_k:Number(p("#candidateK").value),strategy:p("#strategy").value})});_(r,e),u.latestCompareReport=e.report;const s=e.report?.baselines?.find(n=>n.strategy===p("#strategy").value)||e.report?.baselines?.[e.report?.baselines?.length-1];s&&(u.latestRetrievalMetrics=s),P()}catch(e){r.textContent=`compare 失败：${e.message}`}});p("#runGenerationEval").addEventListener("click",async()=>{const r=p("#evalResult");r.textContent="正在运行 generation eval...";try{const e=await E("/eval/generation",{method:"POST",body:JSON.stringify({candidate_k:Number(p("#candidateK").value)})});_(r,e)}catch(e){r.textContent=`generation eval 失败：${e.message}`}});p("#runBenchmark").addEventListener("click",async()=>{const r=p("#evalResult");r.textContent="正在运行 system benchmark...";try{const e=await E("/eval/benchmark",{method:"POST",body:JSON.stringify({candidate_k:Number(p("#candidateK").value)})});_(r,e),u.latestBenchmarkMetrics=e.metrics,P()}catch(e){r.textContent=`benchmark 失败：${e.message}`}});oe();P();
