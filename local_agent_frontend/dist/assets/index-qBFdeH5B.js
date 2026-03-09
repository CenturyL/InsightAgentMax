(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))s(n);new MutationObserver(n=>{for(const l of n)if(l.type==="childList")for(const a of l.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&s(a)}).observe(document,{childList:!0,subtree:!0});function r(n){const l={};return n.integrity&&(l.integrity=n.integrity),n.referrerPolicy&&(l.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?l.credentials="include":n.crossOrigin==="anonymous"?l.credentials="omit":l.credentials="same-origin",l}function s(n){if(n.ep)return;n.ep=!0;const l=r(n);fetch(n.href,l)}})();function ee(){return{async:!1,breaks:!1,extensions:null,gfm:!0,hooks:null,pedantic:!1,renderer:null,silent:!1,tokenizer:null,walkTokens:null}}var R=ee();function we(t){R=t}var B={exec:()=>null};function d(t,e=""){let r=typeof t=="string"?t:t.source,s={replace:(n,l)=>{let a=typeof l=="string"?l:l.source;return a=a.replace(x.caret,"$1"),r=r.replace(n,a),s},getRegex:()=>new RegExp(r,e)};return s}var Me=(()=>{try{return!!new RegExp("(?<=1)(?<!1)")}catch{return!1}})(),x={codeRemoveIndent:/^(?: {1,4}| {0,3}\t)/gm,outputLinkReplace:/\\([\[\]])/g,indentCodeCompensation:/^(\s+)(?:```)/,beginningSpace:/^\s+/,endingHash:/#$/,startingSpaceChar:/^ /,endingSpaceChar:/ $/,nonSpaceChar:/[^ ]/,newLineCharGlobal:/\n/g,tabCharGlobal:/\t/g,multipleSpaceGlobal:/\s+/g,blankLine:/^[ \t]*$/,doubleBlankLine:/\n[ \t]*\n[ \t]*$/,blockquoteStart:/^ {0,3}>/,blockquoteSetextReplace:/\n {0,3}((?:=+|-+) *)(?=\n|$)/g,blockquoteSetextReplace2:/^ {0,3}>[ \t]?/gm,listReplaceTabs:/^\t+/,listReplaceNesting:/^ {1,4}(?=( {4})*[^ ])/g,listIsTask:/^\[[ xX]\] /,listReplaceTask:/^\[[ xX]\] +/,anyLine:/\n.*\n/,hrefBrackets:/^<(.*)>$/,tableDelimiter:/[:|]/,tableAlignChars:/^\||\| *$/g,tableRowBlankLine:/\n[ \t]*$/,tableAlignRight:/^ *-+: *$/,tableAlignCenter:/^ *:-+: *$/,tableAlignLeft:/^ *:-+ *$/,startATag:/^<a /i,endATag:/^<\/a>/i,startPreScriptTag:/^<(pre|code|kbd|script)(\s|>)/i,endPreScriptTag:/^<\/(pre|code|kbd|script)(\s|>)/i,startAngleBracket:/^</,endAngleBracket:/>$/,pedanticHrefTitle:/^([^'"]*[^\s])\s+(['"])(.*)\2/,unicodeAlphaNumeric:/[\p{L}\p{N}]/u,escapeTest:/[&<>"']/,escapeReplace:/[&<>"']/g,escapeTestNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/,escapeReplaceNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/g,unescapeTest:/&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig,caret:/(^|[^\[])\^/g,percentDecode:/%25/g,findPipe:/\|/g,splitPipe:/ \|/,slashPipe:/\\\|/g,carriageReturn:/\r\n|\r/g,spaceLine:/^ +$/gm,notSpaceStart:/^\S*/,endingNewline:/\n$/,listItemRegex:t=>new RegExp(`^( {0,3}${t})((?:[	 ][^\\n]*)?(?:\\n|$))`),nextBulletRegex:t=>new RegExp(`^ {0,${Math.min(3,t-1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`),hrRegex:t=>new RegExp(`^ {0,${Math.min(3,t-1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`),fencesBeginRegex:t=>new RegExp(`^ {0,${Math.min(3,t-1)}}(?:\`\`\`|~~~)`),headingBeginRegex:t=>new RegExp(`^ {0,${Math.min(3,t-1)}}#`),htmlBeginRegex:t=>new RegExp(`^ {0,${Math.min(3,t-1)}}<(?:[a-z].*>|!--)`,"i")},Oe=/^(?:[ \t]*(?:\n|$))+/,Ne=/^((?: {4}| {0,3}\t)[^\n]+(?:\n(?:[ \t]*(?:\n|$))*)?)+/,De=/^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/,P=/^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/,He=/^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/,te=/(?:[*+-]|\d{1,9}[.)])/,ye=/^(?!bull |blockCode|fences|blockquote|heading|html|table)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html|table))+?)\n {0,3}(=+|-+) *(?:\n+|$)/,Se=d(ye).replace(/bull/g,te).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/\|table/g,"").getRegex(),Ze=d(ye).replace(/bull/g,te).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/table/g,/ {0,3}\|?(?:[:\- ]*\|)+[\:\- ]*\n/).getRegex(),ne=/^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/,je=/^[^\n]+/,re=/(?!\s*\])(?:\\[\s\S]|[^\[\]\\])+/,Ge=d(/^ {0,3}\[(label)\]: *(?:\n[ \t]*)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n[ \t]*)?| *\n[ \t]*)(title))? *(?:\n+|$)/).replace("label",re).replace("title",/(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(),Ke=d(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g,te).getRegex(),Z="address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul",se=/<!--(?:-?>|[\s\S]*?(?:-->|$))/,Fe=d("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$))","i").replace("comment",se).replace("tag",Z).replace("attribute",/ +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(),$e=d(ne).replace("hr",P).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("|table","").replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",Z).getRegex(),Qe=d(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph",$e).getRegex(),ae={blockquote:Qe,code:Ne,def:Ge,fences:De,heading:He,hr:P,html:Fe,lheading:Se,list:Ke,newline:Oe,paragraph:$e,table:B,text:je},ge=d("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr",P).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("blockquote"," {0,3}>").replace("code","(?: {4}| {0,3}	)[^\\n]").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",Z).getRegex(),Je={...ae,lheading:Ze,table:ge,paragraph:d(ne).replace("hr",P).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("table",ge).replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",Z).getRegex()},Ue={...ae,html:d(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment",se).replace(/tag/g,"(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),def:/^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,heading:/^(#{1,6})(.*)(?:\n+|$)/,fences:B,lheading:/^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,paragraph:d(ne).replace("hr",P).replace("heading",` *#{1,6} *[^
]`).replace("lheading",Se).replace("|table","").replace("blockquote"," {0,3}>").replace("|fences","").replace("|list","").replace("|html","").replace("|tag","").getRegex()},We=/^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/,Xe=/^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/,Re=/^( {2,}|\\)\n(?!\s*$)/,Ve=/^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/,j=/[\p{P}\p{S}]/u,le=/[\s\p{P}\p{S}]/u,Te=/[^\s\p{P}\p{S}]/u,Ye=d(/^((?![*_])punctSpace)/,"u").replace(/punctSpace/g,le).getRegex(),Ce=/(?!~)[\p{P}\p{S}]/u,et=/(?!~)[\s\p{P}\p{S}]/u,tt=/(?:[^\s\p{P}\p{S}]|~)/u,nt=d(/link|precode-code|html/,"g").replace("link",/\[(?:[^\[\]`]|(?<a>`+)[^`]+\k<a>(?!`))*?\]\((?:\\[\s\S]|[^\\\(\)]|\((?:\\[\s\S]|[^\\\(\)])*\))*\)/).replace("precode-",Me?"(?<!`)()":"(^^|[^`])").replace("code",/(?<b>`+)[^`]+\k<b>(?!`)/).replace("html",/<(?! )[^<>]*?>/).getRegex(),_e=/^(?:\*+(?:((?!\*)punct)|[^\s*]))|^_+(?:((?!_)punct)|([^\s_]))/,rt=d(_e,"u").replace(/punct/g,j).getRegex(),st=d(_e,"u").replace(/punct/g,Ce).getRegex(),Ae="^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)punct(\\*+)(?=[\\s]|$)|notPunctSpace(\\*+)(?!\\*)(?=punctSpace|$)|(?!\\*)punctSpace(\\*+)(?=notPunctSpace)|[\\s](\\*+)(?!\\*)(?=punct)|(?!\\*)punct(\\*+)(?!\\*)(?=punct)|notPunctSpace(\\*+)(?=notPunctSpace)",at=d(Ae,"gu").replace(/notPunctSpace/g,Te).replace(/punctSpace/g,le).replace(/punct/g,j).getRegex(),lt=d(Ae,"gu").replace(/notPunctSpace/g,tt).replace(/punctSpace/g,et).replace(/punct/g,Ce).getRegex(),it=d("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)punct(_+)(?=[\\s]|$)|notPunctSpace(_+)(?!_)(?=punctSpace|$)|(?!_)punctSpace(_+)(?=notPunctSpace)|[\\s](_+)(?!_)(?=punct)|(?!_)punct(_+)(?!_)(?=punct)","gu").replace(/notPunctSpace/g,Te).replace(/punctSpace/g,le).replace(/punct/g,j).getRegex(),ot=d(/\\(punct)/,"gu").replace(/punct/g,j).getRegex(),ct=d(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme",/[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email",/[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(),pt=d(se).replace("(?:-->|$)","-->").getRegex(),ht=d("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment",pt).replace("attribute",/\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(),N=/(?:\[(?:\\[\s\S]|[^\[\]\\])*\]|\\[\s\S]|`+[^`]*?`+(?!`)|[^\[\]\\`])*?/,ut=d(/^!?\[(label)\]\(\s*(href)(?:(?:[ \t]*(?:\n[ \t]*)?)(title))?\s*\)/).replace("label",N).replace("href",/<(?:\\.|[^\n<>\\])+>|[^ \t\n\x00-\x1f]*/).replace("title",/"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(),Ee=d(/^!?\[(label)\]\[(ref)\]/).replace("label",N).replace("ref",re).getRegex(),Le=d(/^!?\[(ref)\](?:\[\])?/).replace("ref",re).getRegex(),dt=d("reflink|nolink(?!\\()","g").replace("reflink",Ee).replace("nolink",Le).getRegex(),ke=/[hH][tT][tT][pP][sS]?|[fF][tT][pP]/,ie={_backpedal:B,anyPunctuation:ot,autolink:ct,blockSkip:nt,br:Re,code:Xe,del:B,emStrongLDelim:rt,emStrongRDelimAst:at,emStrongRDelimUnd:it,escape:We,link:ut,nolink:Le,punctuation:Ye,reflink:Ee,reflinkSearch:dt,tag:ht,text:Ve,url:B},gt={...ie,link:d(/^!?\[(label)\]\((.*?)\)/).replace("label",N).getRegex(),reflink:d(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label",N).getRegex()},J={...ie,emStrongRDelimAst:lt,emStrongLDelim:st,url:d(/^((?:protocol):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/).replace("protocol",ke).replace("email",/[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),_backpedal:/(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,del:/^(~~?)(?=[^\s~])((?:\\[\s\S]|[^\\])*?(?:\\[\s\S]|[^\s~\\]))\1(?=[^~]|$)/,text:d(/^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|protocol:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/).replace("protocol",ke).getRegex()},kt={...J,br:d(Re).replace("{2,}","*").getRegex(),text:d(J.text).replace("\\b_","\\b_| {2,}\\n").replace(/\{2,\}/g,"*").getRegex()},q={normal:ae,gfm:Je,pedantic:Ue},A={normal:ie,gfm:J,breaks:kt,pedantic:gt},ft={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"},fe=t=>ft[t];function S(t,e){if(e){if(x.escapeTest.test(t))return t.replace(x.escapeReplace,fe)}else if(x.escapeTestNoEncode.test(t))return t.replace(x.escapeReplaceNoEncode,fe);return t}function me(t){try{t=encodeURI(t).replace(x.percentDecode,"%")}catch{return null}return t}function be(t,e){let r=t.replace(x.findPipe,(l,a,o)=>{let i=!1,u=a;for(;--u>=0&&o[u]==="\\";)i=!i;return i?"|":" |"}),s=r.split(x.splitPipe),n=0;if(s[0].trim()||s.shift(),s.length>0&&!s.at(-1)?.trim()&&s.pop(),e)if(s.length>e)s.splice(e);else for(;s.length<e;)s.push("");for(;n<s.length;n++)s[n]=s[n].trim().replace(x.slashPipe,"|");return s}function E(t,e,r){let s=t.length;if(s===0)return"";let n=0;for(;n<s&&t.charAt(s-n-1)===e;)n++;return t.slice(0,s-n)}function mt(t,e){if(t.indexOf(e[1])===-1)return-1;let r=0;for(let s=0;s<t.length;s++)if(t[s]==="\\")s++;else if(t[s]===e[0])r++;else if(t[s]===e[1]&&(r--,r<0))return s;return r>0?-2:-1}function xe(t,e,r,s,n){let l=e.href,a=e.title||null,o=t[1].replace(n.other.outputLinkReplace,"$1");s.state.inLink=!0;let i={type:t[0].charAt(0)==="!"?"image":"link",raw:r,href:l,title:a,text:o,tokens:s.inlineTokens(o)};return s.state.inLink=!1,i}function bt(t,e,r){let s=t.match(r.other.indentCodeCompensation);if(s===null)return e;let n=s[1];return e.split(`
`).map(l=>{let a=l.match(r.other.beginningSpace);if(a===null)return l;let[o]=a;return o.length>=n.length?l.slice(n.length):l}).join(`
`)}var D=class{options;rules;lexer;constructor(t){this.options=t||R}space(t){let e=this.rules.block.newline.exec(t);if(e&&e[0].length>0)return{type:"space",raw:e[0]}}code(t){let e=this.rules.block.code.exec(t);if(e){let r=e[0].replace(this.rules.other.codeRemoveIndent,"");return{type:"code",raw:e[0],codeBlockStyle:"indented",text:this.options.pedantic?r:E(r,`
`)}}}fences(t){let e=this.rules.block.fences.exec(t);if(e){let r=e[0],s=bt(r,e[3]||"",this.rules);return{type:"code",raw:r,lang:e[2]?e[2].trim().replace(this.rules.inline.anyPunctuation,"$1"):e[2],text:s}}}heading(t){let e=this.rules.block.heading.exec(t);if(e){let r=e[2].trim();if(this.rules.other.endingHash.test(r)){let s=E(r,"#");(this.options.pedantic||!s||this.rules.other.endingSpaceChar.test(s))&&(r=s.trim())}return{type:"heading",raw:e[0],depth:e[1].length,text:r,tokens:this.lexer.inline(r)}}}hr(t){let e=this.rules.block.hr.exec(t);if(e)return{type:"hr",raw:E(e[0],`
`)}}blockquote(t){let e=this.rules.block.blockquote.exec(t);if(e){let r=E(e[0],`
`).split(`
`),s="",n="",l=[];for(;r.length>0;){let a=!1,o=[],i;for(i=0;i<r.length;i++)if(this.rules.other.blockquoteStart.test(r[i]))o.push(r[i]),a=!0;else if(!a)o.push(r[i]);else break;r=r.slice(i);let u=o.join(`
`),p=u.replace(this.rules.other.blockquoteSetextReplace,`
    $1`).replace(this.rules.other.blockquoteSetextReplace2,"");s=s?`${s}
${u}`:u,n=n?`${n}
${p}`:p;let f=this.lexer.state.top;if(this.lexer.state.top=!0,this.lexer.blockTokens(p,l,!0),this.lexer.state.top=f,r.length===0)break;let g=l.at(-1);if(g?.type==="code")break;if(g?.type==="blockquote"){let b=g,m=b.raw+`
`+r.join(`
`),v=this.blockquote(m);l[l.length-1]=v,s=s.substring(0,s.length-b.raw.length)+v.raw,n=n.substring(0,n.length-b.text.length)+v.text;break}else if(g?.type==="list"){let b=g,m=b.raw+`
`+r.join(`
`),v=this.list(m);l[l.length-1]=v,s=s.substring(0,s.length-g.raw.length)+v.raw,n=n.substring(0,n.length-b.raw.length)+v.raw,r=m.substring(l.at(-1).raw.length).split(`
`);continue}}return{type:"blockquote",raw:s,tokens:l,text:n}}}list(t){let e=this.rules.block.list.exec(t);if(e){let r=e[1].trim(),s=r.length>1,n={type:"list",raw:"",ordered:s,start:s?+r.slice(0,-1):"",loose:!1,items:[]};r=s?`\\d{1,9}\\${r.slice(-1)}`:`\\${r}`,this.options.pedantic&&(r=s?r:"[*+-]");let l=this.rules.other.listItemRegex(r),a=!1;for(;t;){let i=!1,u="",p="";if(!(e=l.exec(t))||this.rules.block.hr.test(t))break;u=e[0],t=t.substring(u.length);let f=e[2].split(`
`,1)[0].replace(this.rules.other.listReplaceTabs,K=>" ".repeat(3*K.length)),g=t.split(`
`,1)[0],b=!f.trim(),m=0;if(this.options.pedantic?(m=2,p=f.trimStart()):b?m=e[1].length+1:(m=e[2].search(this.rules.other.nonSpaceChar),m=m>4?1:m,p=f.slice(m),m+=e[1].length),b&&this.rules.other.blankLine.test(g)&&(u+=g+`
`,t=t.substring(g.length+1),i=!0),!i){let K=this.rules.other.nextBulletRegex(m),he=this.rules.other.hrRegex(m),ue=this.rules.other.fencesBeginRegex(m),de=this.rules.other.headingBeginRegex(m),qe=this.rules.other.htmlBeginRegex(m);for(;t;){let F=t.split(`
`,1)[0],_;if(g=F,this.options.pedantic?(g=g.replace(this.rules.other.listReplaceNesting,"  "),_=g):_=g.replace(this.rules.other.tabCharGlobal,"    "),ue.test(g)||de.test(g)||qe.test(g)||K.test(g)||he.test(g))break;if(_.search(this.rules.other.nonSpaceChar)>=m||!g.trim())p+=`
`+_.slice(m);else{if(b||f.replace(this.rules.other.tabCharGlobal,"    ").search(this.rules.other.nonSpaceChar)>=4||ue.test(f)||de.test(f)||he.test(f))break;p+=`
`+g}!b&&!g.trim()&&(b=!0),u+=F+`
`,t=t.substring(F.length+1),f=_.slice(m)}}n.loose||(a?n.loose=!0:this.rules.other.doubleBlankLine.test(u)&&(a=!0));let v=null,pe;this.options.gfm&&(v=this.rules.other.listIsTask.exec(p),v&&(pe=v[0]!=="[ ] ",p=p.replace(this.rules.other.listReplaceTask,""))),n.items.push({type:"list_item",raw:u,task:!!v,checked:pe,loose:!1,text:p,tokens:[]}),n.raw+=u}let o=n.items.at(-1);if(o)o.raw=o.raw.trimEnd(),o.text=o.text.trimEnd();else return;n.raw=n.raw.trimEnd();for(let i=0;i<n.items.length;i++)if(this.lexer.state.top=!1,n.items[i].tokens=this.lexer.blockTokens(n.items[i].text,[]),!n.loose){let u=n.items[i].tokens.filter(f=>f.type==="space"),p=u.length>0&&u.some(f=>this.rules.other.anyLine.test(f.raw));n.loose=p}if(n.loose)for(let i=0;i<n.items.length;i++)n.items[i].loose=!0;return n}}html(t){let e=this.rules.block.html.exec(t);if(e)return{type:"html",block:!0,raw:e[0],pre:e[1]==="pre"||e[1]==="script"||e[1]==="style",text:e[0]}}def(t){let e=this.rules.block.def.exec(t);if(e){let r=e[1].toLowerCase().replace(this.rules.other.multipleSpaceGlobal," "),s=e[2]?e[2].replace(this.rules.other.hrefBrackets,"$1").replace(this.rules.inline.anyPunctuation,"$1"):"",n=e[3]?e[3].substring(1,e[3].length-1).replace(this.rules.inline.anyPunctuation,"$1"):e[3];return{type:"def",tag:r,raw:e[0],href:s,title:n}}}table(t){let e=this.rules.block.table.exec(t);if(!e||!this.rules.other.tableDelimiter.test(e[2]))return;let r=be(e[1]),s=e[2].replace(this.rules.other.tableAlignChars,"").split("|"),n=e[3]?.trim()?e[3].replace(this.rules.other.tableRowBlankLine,"").split(`
`):[],l={type:"table",raw:e[0],header:[],align:[],rows:[]};if(r.length===s.length){for(let a of s)this.rules.other.tableAlignRight.test(a)?l.align.push("right"):this.rules.other.tableAlignCenter.test(a)?l.align.push("center"):this.rules.other.tableAlignLeft.test(a)?l.align.push("left"):l.align.push(null);for(let a=0;a<r.length;a++)l.header.push({text:r[a],tokens:this.lexer.inline(r[a]),header:!0,align:l.align[a]});for(let a of n)l.rows.push(be(a,l.header.length).map((o,i)=>({text:o,tokens:this.lexer.inline(o),header:!1,align:l.align[i]})));return l}}lheading(t){let e=this.rules.block.lheading.exec(t);if(e)return{type:"heading",raw:e[0],depth:e[2].charAt(0)==="="?1:2,text:e[1],tokens:this.lexer.inline(e[1])}}paragraph(t){let e=this.rules.block.paragraph.exec(t);if(e){let r=e[1].charAt(e[1].length-1)===`
`?e[1].slice(0,-1):e[1];return{type:"paragraph",raw:e[0],text:r,tokens:this.lexer.inline(r)}}}text(t){let e=this.rules.block.text.exec(t);if(e)return{type:"text",raw:e[0],text:e[0],tokens:this.lexer.inline(e[0])}}escape(t){let e=this.rules.inline.escape.exec(t);if(e)return{type:"escape",raw:e[0],text:e[1]}}tag(t){let e=this.rules.inline.tag.exec(t);if(e)return!this.lexer.state.inLink&&this.rules.other.startATag.test(e[0])?this.lexer.state.inLink=!0:this.lexer.state.inLink&&this.rules.other.endATag.test(e[0])&&(this.lexer.state.inLink=!1),!this.lexer.state.inRawBlock&&this.rules.other.startPreScriptTag.test(e[0])?this.lexer.state.inRawBlock=!0:this.lexer.state.inRawBlock&&this.rules.other.endPreScriptTag.test(e[0])&&(this.lexer.state.inRawBlock=!1),{type:"html",raw:e[0],inLink:this.lexer.state.inLink,inRawBlock:this.lexer.state.inRawBlock,block:!1,text:e[0]}}link(t){let e=this.rules.inline.link.exec(t);if(e){let r=e[2].trim();if(!this.options.pedantic&&this.rules.other.startAngleBracket.test(r)){if(!this.rules.other.endAngleBracket.test(r))return;let l=E(r.slice(0,-1),"\\");if((r.length-l.length)%2===0)return}else{let l=mt(e[2],"()");if(l===-2)return;if(l>-1){let a=(e[0].indexOf("!")===0?5:4)+e[1].length+l;e[2]=e[2].substring(0,l),e[0]=e[0].substring(0,a).trim(),e[3]=""}}let s=e[2],n="";if(this.options.pedantic){let l=this.rules.other.pedanticHrefTitle.exec(s);l&&(s=l[1],n=l[3])}else n=e[3]?e[3].slice(1,-1):"";return s=s.trim(),this.rules.other.startAngleBracket.test(s)&&(this.options.pedantic&&!this.rules.other.endAngleBracket.test(r)?s=s.slice(1):s=s.slice(1,-1)),xe(e,{href:s&&s.replace(this.rules.inline.anyPunctuation,"$1"),title:n&&n.replace(this.rules.inline.anyPunctuation,"$1")},e[0],this.lexer,this.rules)}}reflink(t,e){let r;if((r=this.rules.inline.reflink.exec(t))||(r=this.rules.inline.nolink.exec(t))){let s=(r[2]||r[1]).replace(this.rules.other.multipleSpaceGlobal," "),n=e[s.toLowerCase()];if(!n){let l=r[0].charAt(0);return{type:"text",raw:l,text:l}}return xe(r,n,r[0],this.lexer,this.rules)}}emStrong(t,e,r=""){let s=this.rules.inline.emStrongLDelim.exec(t);if(!(!s||s[3]&&r.match(this.rules.other.unicodeAlphaNumeric))&&(!(s[1]||s[2])||!r||this.rules.inline.punctuation.exec(r))){let n=[...s[0]].length-1,l,a,o=n,i=0,u=s[0][0]==="*"?this.rules.inline.emStrongRDelimAst:this.rules.inline.emStrongRDelimUnd;for(u.lastIndex=0,e=e.slice(-1*t.length+n);(s=u.exec(e))!=null;){if(l=s[1]||s[2]||s[3]||s[4]||s[5]||s[6],!l)continue;if(a=[...l].length,s[3]||s[4]){o+=a;continue}else if((s[5]||s[6])&&n%3&&!((n+a)%3)){i+=a;continue}if(o-=a,o>0)continue;a=Math.min(a,a+o+i);let p=[...s[0]][0].length,f=t.slice(0,n+s.index+p+a);if(Math.min(n,a)%2){let b=f.slice(1,-1);return{type:"em",raw:f,text:b,tokens:this.lexer.inlineTokens(b)}}let g=f.slice(2,-2);return{type:"strong",raw:f,text:g,tokens:this.lexer.inlineTokens(g)}}}}codespan(t){let e=this.rules.inline.code.exec(t);if(e){let r=e[2].replace(this.rules.other.newLineCharGlobal," "),s=this.rules.other.nonSpaceChar.test(r),n=this.rules.other.startingSpaceChar.test(r)&&this.rules.other.endingSpaceChar.test(r);return s&&n&&(r=r.substring(1,r.length-1)),{type:"codespan",raw:e[0],text:r}}}br(t){let e=this.rules.inline.br.exec(t);if(e)return{type:"br",raw:e[0]}}del(t){let e=this.rules.inline.del.exec(t);if(e)return{type:"del",raw:e[0],text:e[2],tokens:this.lexer.inlineTokens(e[2])}}autolink(t){let e=this.rules.inline.autolink.exec(t);if(e){let r,s;return e[2]==="@"?(r=e[1],s="mailto:"+r):(r=e[1],s=r),{type:"link",raw:e[0],text:r,href:s,tokens:[{type:"text",raw:r,text:r}]}}}url(t){let e;if(e=this.rules.inline.url.exec(t)){let r,s;if(e[2]==="@")r=e[0],s="mailto:"+r;else{let n;do n=e[0],e[0]=this.rules.inline._backpedal.exec(e[0])?.[0]??"";while(n!==e[0]);r=e[0],e[1]==="www."?s="http://"+e[0]:s=e[0]}return{type:"link",raw:e[0],text:r,href:s,tokens:[{type:"text",raw:r,text:r}]}}}inlineText(t){let e=this.rules.inline.text.exec(t);if(e){let r=this.lexer.state.inRawBlock;return{type:"text",raw:e[0],text:e[0],escaped:r}}}},w=class U{tokens;options;state;tokenizer;inlineQueue;constructor(e){this.tokens=[],this.tokens.links=Object.create(null),this.options=e||R,this.options.tokenizer=this.options.tokenizer||new D,this.tokenizer=this.options.tokenizer,this.tokenizer.options=this.options,this.tokenizer.lexer=this,this.inlineQueue=[],this.state={inLink:!1,inRawBlock:!1,top:!0};let r={other:x,block:q.normal,inline:A.normal};this.options.pedantic?(r.block=q.pedantic,r.inline=A.pedantic):this.options.gfm&&(r.block=q.gfm,this.options.breaks?r.inline=A.breaks:r.inline=A.gfm),this.tokenizer.rules=r}static get rules(){return{block:q,inline:A}}static lex(e,r){return new U(r).lex(e)}static lexInline(e,r){return new U(r).inlineTokens(e)}lex(e){e=e.replace(x.carriageReturn,`
`),this.blockTokens(e,this.tokens);for(let r=0;r<this.inlineQueue.length;r++){let s=this.inlineQueue[r];this.inlineTokens(s.src,s.tokens)}return this.inlineQueue=[],this.tokens}blockTokens(e,r=[],s=!1){for(this.options.pedantic&&(e=e.replace(x.tabCharGlobal,"    ").replace(x.spaceLine,""));e;){let n;if(this.options.extensions?.block?.some(a=>(n=a.call({lexer:this},e,r))?(e=e.substring(n.raw.length),r.push(n),!0):!1))continue;if(n=this.tokenizer.space(e)){e=e.substring(n.raw.length);let a=r.at(-1);n.raw.length===1&&a!==void 0?a.raw+=`
`:r.push(n);continue}if(n=this.tokenizer.code(e)){e=e.substring(n.raw.length);let a=r.at(-1);a?.type==="paragraph"||a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+n.raw,a.text+=`
`+n.text,this.inlineQueue.at(-1).src=a.text):r.push(n);continue}if(n=this.tokenizer.fences(e)){e=e.substring(n.raw.length),r.push(n);continue}if(n=this.tokenizer.heading(e)){e=e.substring(n.raw.length),r.push(n);continue}if(n=this.tokenizer.hr(e)){e=e.substring(n.raw.length),r.push(n);continue}if(n=this.tokenizer.blockquote(e)){e=e.substring(n.raw.length),r.push(n);continue}if(n=this.tokenizer.list(e)){e=e.substring(n.raw.length),r.push(n);continue}if(n=this.tokenizer.html(e)){e=e.substring(n.raw.length),r.push(n);continue}if(n=this.tokenizer.def(e)){e=e.substring(n.raw.length);let a=r.at(-1);a?.type==="paragraph"||a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+n.raw,a.text+=`
`+n.raw,this.inlineQueue.at(-1).src=a.text):this.tokens.links[n.tag]||(this.tokens.links[n.tag]={href:n.href,title:n.title},r.push(n));continue}if(n=this.tokenizer.table(e)){e=e.substring(n.raw.length),r.push(n);continue}if(n=this.tokenizer.lheading(e)){e=e.substring(n.raw.length),r.push(n);continue}let l=e;if(this.options.extensions?.startBlock){let a=1/0,o=e.slice(1),i;this.options.extensions.startBlock.forEach(u=>{i=u.call({lexer:this},o),typeof i=="number"&&i>=0&&(a=Math.min(a,i))}),a<1/0&&a>=0&&(l=e.substring(0,a+1))}if(this.state.top&&(n=this.tokenizer.paragraph(l))){let a=r.at(-1);s&&a?.type==="paragraph"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+n.raw,a.text+=`
`+n.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=a.text):r.push(n),s=l.length!==e.length,e=e.substring(n.raw.length);continue}if(n=this.tokenizer.text(e)){e=e.substring(n.raw.length);let a=r.at(-1);a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+n.raw,a.text+=`
`+n.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=a.text):r.push(n);continue}if(e){let a="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(a);break}else throw new Error(a)}}return this.state.top=!0,r}inline(e,r=[]){return this.inlineQueue.push({src:e,tokens:r}),r}inlineTokens(e,r=[]){let s=e,n=null;if(this.tokens.links){let i=Object.keys(this.tokens.links);if(i.length>0)for(;(n=this.tokenizer.rules.inline.reflinkSearch.exec(s))!=null;)i.includes(n[0].slice(n[0].lastIndexOf("[")+1,-1))&&(s=s.slice(0,n.index)+"["+"a".repeat(n[0].length-2)+"]"+s.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex))}for(;(n=this.tokenizer.rules.inline.anyPunctuation.exec(s))!=null;)s=s.slice(0,n.index)+"++"+s.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);let l;for(;(n=this.tokenizer.rules.inline.blockSkip.exec(s))!=null;)l=n[2]?n[2].length:0,s=s.slice(0,n.index+l)+"["+"a".repeat(n[0].length-l-2)+"]"+s.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);s=this.options.hooks?.emStrongMask?.call({lexer:this},s)??s;let a=!1,o="";for(;e;){a||(o=""),a=!1;let i;if(this.options.extensions?.inline?.some(p=>(i=p.call({lexer:this},e,r))?(e=e.substring(i.raw.length),r.push(i),!0):!1))continue;if(i=this.tokenizer.escape(e)){e=e.substring(i.raw.length),r.push(i);continue}if(i=this.tokenizer.tag(e)){e=e.substring(i.raw.length),r.push(i);continue}if(i=this.tokenizer.link(e)){e=e.substring(i.raw.length),r.push(i);continue}if(i=this.tokenizer.reflink(e,this.tokens.links)){e=e.substring(i.raw.length);let p=r.at(-1);i.type==="text"&&p?.type==="text"?(p.raw+=i.raw,p.text+=i.text):r.push(i);continue}if(i=this.tokenizer.emStrong(e,s,o)){e=e.substring(i.raw.length),r.push(i);continue}if(i=this.tokenizer.codespan(e)){e=e.substring(i.raw.length),r.push(i);continue}if(i=this.tokenizer.br(e)){e=e.substring(i.raw.length),r.push(i);continue}if(i=this.tokenizer.del(e)){e=e.substring(i.raw.length),r.push(i);continue}if(i=this.tokenizer.autolink(e)){e=e.substring(i.raw.length),r.push(i);continue}if(!this.state.inLink&&(i=this.tokenizer.url(e))){e=e.substring(i.raw.length),r.push(i);continue}let u=e;if(this.options.extensions?.startInline){let p=1/0,f=e.slice(1),g;this.options.extensions.startInline.forEach(b=>{g=b.call({lexer:this},f),typeof g=="number"&&g>=0&&(p=Math.min(p,g))}),p<1/0&&p>=0&&(u=e.substring(0,p+1))}if(i=this.tokenizer.inlineText(u)){e=e.substring(i.raw.length),i.raw.slice(-1)!=="_"&&(o=i.raw.slice(-1)),a=!0;let p=r.at(-1);p?.type==="text"?(p.raw+=i.raw,p.text+=i.text):r.push(i);continue}if(e){let p="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(p);break}else throw new Error(p)}}return r}},H=class{options;parser;constructor(t){this.options=t||R}space(t){return""}code({text:t,lang:e,escaped:r}){let s=(e||"").match(x.notSpaceStart)?.[0],n=t.replace(x.endingNewline,"")+`
`;return s?'<pre><code class="language-'+S(s)+'">'+(r?n:S(n,!0))+`</code></pre>
`:"<pre><code>"+(r?n:S(n,!0))+`</code></pre>
`}blockquote({tokens:t}){return`<blockquote>
${this.parser.parse(t)}</blockquote>
`}html({text:t}){return t}def(t){return""}heading({tokens:t,depth:e}){return`<h${e}>${this.parser.parseInline(t)}</h${e}>
`}hr(t){return`<hr>
`}list(t){let e=t.ordered,r=t.start,s="";for(let a=0;a<t.items.length;a++){let o=t.items[a];s+=this.listitem(o)}let n=e?"ol":"ul",l=e&&r!==1?' start="'+r+'"':"";return"<"+n+l+`>
`+s+"</"+n+`>
`}listitem(t){let e="";if(t.task){let r=this.checkbox({checked:!!t.checked});t.loose?t.tokens[0]?.type==="paragraph"?(t.tokens[0].text=r+" "+t.tokens[0].text,t.tokens[0].tokens&&t.tokens[0].tokens.length>0&&t.tokens[0].tokens[0].type==="text"&&(t.tokens[0].tokens[0].text=r+" "+S(t.tokens[0].tokens[0].text),t.tokens[0].tokens[0].escaped=!0)):t.tokens.unshift({type:"text",raw:r+" ",text:r+" ",escaped:!0}):e+=r+" "}return e+=this.parser.parse(t.tokens,!!t.loose),`<li>${e}</li>
`}checkbox({checked:t}){return"<input "+(t?'checked="" ':"")+'disabled="" type="checkbox">'}paragraph({tokens:t}){return`<p>${this.parser.parseInline(t)}</p>
`}table(t){let e="",r="";for(let n=0;n<t.header.length;n++)r+=this.tablecell(t.header[n]);e+=this.tablerow({text:r});let s="";for(let n=0;n<t.rows.length;n++){let l=t.rows[n];r="";for(let a=0;a<l.length;a++)r+=this.tablecell(l[a]);s+=this.tablerow({text:r})}return s&&(s=`<tbody>${s}</tbody>`),`<table>
<thead>
`+e+`</thead>
`+s+`</table>
`}tablerow({text:t}){return`<tr>
${t}</tr>
`}tablecell(t){let e=this.parser.parseInline(t.tokens),r=t.header?"th":"td";return(t.align?`<${r} align="${t.align}">`:`<${r}>`)+e+`</${r}>
`}strong({tokens:t}){return`<strong>${this.parser.parseInline(t)}</strong>`}em({tokens:t}){return`<em>${this.parser.parseInline(t)}</em>`}codespan({text:t}){return`<code>${S(t,!0)}</code>`}br(t){return"<br>"}del({tokens:t}){return`<del>${this.parser.parseInline(t)}</del>`}link({href:t,title:e,tokens:r}){let s=this.parser.parseInline(r),n=me(t);if(n===null)return s;t=n;let l='<a href="'+t+'"';return e&&(l+=' title="'+S(e)+'"'),l+=">"+s+"</a>",l}image({href:t,title:e,text:r,tokens:s}){s&&(r=this.parser.parseInline(s,this.parser.textRenderer));let n=me(t);if(n===null)return S(r);t=n;let l=`<img src="${t}" alt="${r}"`;return e&&(l+=` title="${S(e)}"`),l+=">",l}text(t){return"tokens"in t&&t.tokens?this.parser.parseInline(t.tokens):"escaped"in t&&t.escaped?t.text:S(t.text)}},oe=class{strong({text:e}){return e}em({text:e}){return e}codespan({text:e}){return e}del({text:e}){return e}html({text:e}){return e}text({text:e}){return e}link({text:e}){return""+e}image({text:e}){return""+e}br(){return""}},y=class W{options;renderer;textRenderer;constructor(e){this.options=e||R,this.options.renderer=this.options.renderer||new H,this.renderer=this.options.renderer,this.renderer.options=this.options,this.renderer.parser=this,this.textRenderer=new oe}static parse(e,r){return new W(r).parse(e)}static parseInline(e,r){return new W(r).parseInline(e)}parse(e,r=!0){let s="";for(let n=0;n<e.length;n++){let l=e[n];if(this.options.extensions?.renderers?.[l.type]){let o=l,i=this.options.extensions.renderers[o.type].call({parser:this},o);if(i!==!1||!["space","hr","heading","code","table","blockquote","list","html","def","paragraph","text"].includes(o.type)){s+=i||"";continue}}let a=l;switch(a.type){case"space":{s+=this.renderer.space(a);continue}case"hr":{s+=this.renderer.hr(a);continue}case"heading":{s+=this.renderer.heading(a);continue}case"code":{s+=this.renderer.code(a);continue}case"table":{s+=this.renderer.table(a);continue}case"blockquote":{s+=this.renderer.blockquote(a);continue}case"list":{s+=this.renderer.list(a);continue}case"html":{s+=this.renderer.html(a);continue}case"def":{s+=this.renderer.def(a);continue}case"paragraph":{s+=this.renderer.paragraph(a);continue}case"text":{let o=a,i=this.renderer.text(o);for(;n+1<e.length&&e[n+1].type==="text";)o=e[++n],i+=`
`+this.renderer.text(o);r?s+=this.renderer.paragraph({type:"paragraph",raw:i,text:i,tokens:[{type:"text",raw:i,text:i,escaped:!0}]}):s+=i;continue}default:{let o='Token with "'+a.type+'" type was not found.';if(this.options.silent)return console.error(o),"";throw new Error(o)}}}return s}parseInline(e,r=this.renderer){let s="";for(let n=0;n<e.length;n++){let l=e[n];if(this.options.extensions?.renderers?.[l.type]){let o=this.options.extensions.renderers[l.type].call({parser:this},l);if(o!==!1||!["escape","html","link","image","strong","em","codespan","br","del","text"].includes(l.type)){s+=o||"";continue}}let a=l;switch(a.type){case"escape":{s+=r.text(a);break}case"html":{s+=r.html(a);break}case"link":{s+=r.link(a);break}case"image":{s+=r.image(a);break}case"strong":{s+=r.strong(a);break}case"em":{s+=r.em(a);break}case"codespan":{s+=r.codespan(a);break}case"br":{s+=r.br(a);break}case"del":{s+=r.del(a);break}case"text":{s+=r.text(a);break}default:{let o='Token with "'+a.type+'" type was not found.';if(this.options.silent)return console.error(o),"";throw new Error(o)}}}return s}},L=class{options;block;constructor(t){this.options=t||R}static passThroughHooks=new Set(["preprocess","postprocess","processAllTokens","emStrongMask"]);static passThroughHooksRespectAsync=new Set(["preprocess","postprocess","processAllTokens"]);preprocess(t){return t}postprocess(t){return t}processAllTokens(t){return t}emStrongMask(t){return t}provideLexer(){return this.block?w.lex:w.lexInline}provideParser(){return this.block?y.parse:y.parseInline}},xt=class{defaults=ee();options=this.setOptions;parse=this.parseMarkdown(!0);parseInline=this.parseMarkdown(!1);Parser=y;Renderer=H;TextRenderer=oe;Lexer=w;Tokenizer=D;Hooks=L;constructor(...t){this.use(...t)}walkTokens(t,e){let r=[];for(let s of t)switch(r=r.concat(e.call(this,s)),s.type){case"table":{let n=s;for(let l of n.header)r=r.concat(this.walkTokens(l.tokens,e));for(let l of n.rows)for(let a of l)r=r.concat(this.walkTokens(a.tokens,e));break}case"list":{let n=s;r=r.concat(this.walkTokens(n.items,e));break}default:{let n=s;this.defaults.extensions?.childTokens?.[n.type]?this.defaults.extensions.childTokens[n.type].forEach(l=>{let a=n[l].flat(1/0);r=r.concat(this.walkTokens(a,e))}):n.tokens&&(r=r.concat(this.walkTokens(n.tokens,e)))}}return r}use(...t){let e=this.defaults.extensions||{renderers:{},childTokens:{}};return t.forEach(r=>{let s={...r};if(s.async=this.defaults.async||s.async||!1,r.extensions&&(r.extensions.forEach(n=>{if(!n.name)throw new Error("extension name required");if("renderer"in n){let l=e.renderers[n.name];l?e.renderers[n.name]=function(...a){let o=n.renderer.apply(this,a);return o===!1&&(o=l.apply(this,a)),o}:e.renderers[n.name]=n.renderer}if("tokenizer"in n){if(!n.level||n.level!=="block"&&n.level!=="inline")throw new Error("extension level must be 'block' or 'inline'");let l=e[n.level];l?l.unshift(n.tokenizer):e[n.level]=[n.tokenizer],n.start&&(n.level==="block"?e.startBlock?e.startBlock.push(n.start):e.startBlock=[n.start]:n.level==="inline"&&(e.startInline?e.startInline.push(n.start):e.startInline=[n.start]))}"childTokens"in n&&n.childTokens&&(e.childTokens[n.name]=n.childTokens)}),s.extensions=e),r.renderer){let n=this.defaults.renderer||new H(this.defaults);for(let l in r.renderer){if(!(l in n))throw new Error(`renderer '${l}' does not exist`);if(["options","parser"].includes(l))continue;let a=l,o=r.renderer[a],i=n[a];n[a]=(...u)=>{let p=o.apply(n,u);return p===!1&&(p=i.apply(n,u)),p||""}}s.renderer=n}if(r.tokenizer){let n=this.defaults.tokenizer||new D(this.defaults);for(let l in r.tokenizer){if(!(l in n))throw new Error(`tokenizer '${l}' does not exist`);if(["options","rules","lexer"].includes(l))continue;let a=l,o=r.tokenizer[a],i=n[a];n[a]=(...u)=>{let p=o.apply(n,u);return p===!1&&(p=i.apply(n,u)),p}}s.tokenizer=n}if(r.hooks){let n=this.defaults.hooks||new L;for(let l in r.hooks){if(!(l in n))throw new Error(`hook '${l}' does not exist`);if(["options","block"].includes(l))continue;let a=l,o=r.hooks[a],i=n[a];L.passThroughHooks.has(l)?n[a]=u=>{if(this.defaults.async&&L.passThroughHooksRespectAsync.has(l))return(async()=>{let f=await o.call(n,u);return i.call(n,f)})();let p=o.call(n,u);return i.call(n,p)}:n[a]=(...u)=>{if(this.defaults.async)return(async()=>{let f=await o.apply(n,u);return f===!1&&(f=await i.apply(n,u)),f})();let p=o.apply(n,u);return p===!1&&(p=i.apply(n,u)),p}}s.hooks=n}if(r.walkTokens){let n=this.defaults.walkTokens,l=r.walkTokens;s.walkTokens=function(a){let o=[];return o.push(l.call(this,a)),n&&(o=o.concat(n.call(this,a))),o}}this.defaults={...this.defaults,...s}}),this}setOptions(t){return this.defaults={...this.defaults,...t},this}lexer(t,e){return w.lex(t,e??this.defaults)}parser(t,e){return y.parse(t,e??this.defaults)}parseMarkdown(t){return(e,r)=>{let s={...r},n={...this.defaults,...s},l=this.onError(!!n.silent,!!n.async);if(this.defaults.async===!0&&s.async===!1)return l(new Error("marked(): The async option was set to true by an extension. Remove async: false from the parse options object to return a Promise."));if(typeof e>"u"||e===null)return l(new Error("marked(): input parameter is undefined or null"));if(typeof e!="string")return l(new Error("marked(): input parameter is of type "+Object.prototype.toString.call(e)+", string expected"));if(n.hooks&&(n.hooks.options=n,n.hooks.block=t),n.async)return(async()=>{let a=n.hooks?await n.hooks.preprocess(e):e,o=await(n.hooks?await n.hooks.provideLexer():t?w.lex:w.lexInline)(a,n),i=n.hooks?await n.hooks.processAllTokens(o):o;n.walkTokens&&await Promise.all(this.walkTokens(i,n.walkTokens));let u=await(n.hooks?await n.hooks.provideParser():t?y.parse:y.parseInline)(i,n);return n.hooks?await n.hooks.postprocess(u):u})().catch(l);try{n.hooks&&(e=n.hooks.preprocess(e));let a=(n.hooks?n.hooks.provideLexer():t?w.lex:w.lexInline)(e,n);n.hooks&&(a=n.hooks.processAllTokens(a)),n.walkTokens&&this.walkTokens(a,n.walkTokens);let o=(n.hooks?n.hooks.provideParser():t?y.parse:y.parseInline)(a,n);return n.hooks&&(o=n.hooks.postprocess(o)),o}catch(a){return l(a)}}}onError(t,e){return r=>{if(r.message+=`
Please report this to https://github.com/markedjs/marked.`,t){let s="<p>An error occurred:</p><pre>"+S(r.message+"",!0)+"</pre>";return e?Promise.resolve(s):s}if(e)return Promise.reject(r);throw r}}},$=new xt;function k(t,e){return $.parse(t,e)}k.options=k.setOptions=function(t){return $.setOptions(t),k.defaults=$.defaults,we(k.defaults),k};k.getDefaults=ee;k.defaults=R;k.use=function(...t){return $.use(...t),k.defaults=$.defaults,we(k.defaults),k};k.walkTokens=function(t,e){return $.walkTokens(t,e)};k.parseInline=$.parseInline;k.Parser=y;k.parser=y.parse;k.Renderer=H;k.TextRenderer=oe;k.Lexer=w;k.lexer=w.lex;k.Tokenizer=D;k.Hooks=L;k.parse=k;k.options;k.setOptions;k.use;k.walkTokens;k.parseInline;y.parse;w.lex;function Be(){if(globalThis.crypto?.randomUUID)return globalThis.crypto.randomUUID();const t=Math.random().toString(36).slice(2,10);return`thread-${Date.now()}-${t}`}const vt=Be(),h={apiBase:localStorage.getItem("agent-api-base")||"/api/v1",threadId:localStorage.getItem("agent-thread-id")||vt,messages:[],latestRetrievalMetrics:null,latestCompareReport:null,latestBenchmarkMetrics:null,activeTrace:[],statusTimer:null,requestStartedAt:null,railOpen:!1,activeEvalAction:"runRetrievalEval",streamingAnswer:""};k.setOptions({gfm:!0,breaks:!0});const wt=document.querySelector("#app");wt.innerHTML=`
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark">IA</div>
        <div>
          <p class="eyebrow">Policy And Tender Agent</p>
          <h1>InsightAgent</h1>
        </div>
        <button id="closeRail" class="ghost rail-close">关闭</button>
      </div>

      <div class="stack">
        <label class="field">
          <span>API Base</span>
          <input id="apiBase" value="${h.apiBase}" placeholder="/api/v1" />
        </label>
        <label class="field">
          <span>Thread ID</span>
          <div class="inline">
            <input id="threadId" value="${h.threadId}" />
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
      </div>

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
      <div class="mobile-toolbar">
        <button id="openRail" class="ghost">菜单</button>
      </div>
      <header class="workspace-header">
        <div>
          <p class="eyebrow">Agent Console</p>
          <h2>InsightAgent</h2>
          <p class="hero-text">面向政策通知、招投标公告与本地知识资料分析的多模式 Agent 工作台。</p>
        </div>
      </header>

      <section class="panel chat-panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Chat</p>
            <h3>对话工作区</h3>
          </div>
          <div class="inline compact">
            <button id="clearChat" class="ghost">清空会话</button>
          </div>
        </div>

        <div class="chat-stack">
          <section class="response-card chat-history-card">
            <div class="response-head">
              <p class="eyebrow">Conversation</p>
              <strong>当前回答与历史记录</strong>
            </div>
            <div id="messageList" class="message-list"></div>
          </section>

          <section class="response-card trace-card">
            <div class="response-head">
              <p class="eyebrow">Trace</p>
              <strong>执行过程</strong>
            </div>
            <div id="traceList" class="trace-list">
              <div class="empty-chat">发送一条消息后，这里会显示路由、规划、检索等过程。</div>
            </div>
          </section>

          <section class="response-card composer-card">
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
          <button id="runRetrievalEval" class="ghost">Retrieval Eval</button>
          <button id="runCompare" class="ghost">Baseline Compare</button>
          <button id="runGenerationEval" class="ghost">Generation Eval</button>
          <button id="runBenchmark" class="ghost">System Benchmark</button>
          <button id="showTestingPanel" class="ghost">测试环境重建</button>
        </div>

        <div id="evalStatus" class="live-status eval-status">选择一个评估功能后开始运行。</div>

        <section id="retrievalEvalPanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Metrics</p>
              <h4>Retrieval Eval</h4>
            </div>
          </div>
          <div id="metricCards" class="metric-grid"></div>
          <pre id="retrievalEvalResult" class="result-box large"></pre>
        </section>

        <section id="comparePanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Compare</p>
              <h4>Baseline Compare</h4>
            </div>
          </div>
          <div id="compareChart" class="chart-panel empty-state">运行 Baseline Compare 后显示</div>
          <pre id="compareResult" class="result-box large"></pre>
        </section>

        <section id="generationEvalPanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Generation</p>
              <h4>Generation Eval</h4>
            </div>
          </div>
          <pre id="generationEvalResult" class="result-box large"></pre>
        </section>

        <section id="benchmarkPanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Benchmark</p>
              <h4>System Benchmark</h4>
            </div>
          </div>
          <div id="benchmarkHighlights" class="hero-metrics hero-metrics-1"></div>
          <div id="benchmarkChart" class="chart-panel empty-state">运行 System Benchmark 后显示</div>
          <pre id="benchmarkResult" class="result-box large"></pre>
        </section>

        <section id="testingPanel" class="dashboard-card eval-panel hidden">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Testing</p>
              <h4>测试环境重建</h4>
            </div>
          </div>
          <p class="helper-text">
            用于一键重新下载测试语料、清洗、入库并重建评估集，适合在新环境或测试数据被改乱后快速恢复。
          </p>
          <div class="compact-actions">
            <label class="check">
              <input id="forceDownload" type="checkbox" />
              <span>强制下载：忽略本地缓存，重新抓取测试文档</span>
            </label>
            <label class="check">
              <input id="runRetrievalEvalAfterRebuild" type="checkbox" checked />
              <span>自动评估：重建完成后顺手跑一次 retrieval eval</span>
            </label>
          </div>
          <div class="inline wrap">
            <button id="rebuildEnv">重建环境</button>
          </div>
          <pre id="rebuildResult" class="result-box large"></pre>
        </section>
      </section>
    </main>
  </div>
`;const c=t=>document.querySelector(t),ve=c("#apiBase"),X=c("#threadId");function ce(t){h.railOpen=t,document.body.dataset.railOpen=t?"true":"false"}function T(t){const e=["runRetrievalEval","runCompare","runGenerationEval","runBenchmark","showTestingPanel"];h.activeEvalAction=t,e.forEach(s=>{const n=c("#"+s);n&&n.classList.toggle("is-active",s===t)});const r={runRetrievalEval:"retrievalEvalPanel",runCompare:"comparePanel",runGenerationEval:"generationEvalPanel",runBenchmark:"benchmarkPanel",showTestingPanel:"testingPanel"};Object.values(r).forEach(s=>{c("#"+s)?.classList.add("hidden")}),t&&r[t]&&c("#"+r[t])?.classList.remove("hidden")}function M(t,e=4){return t==null||Number.isNaN(Number(t))?"-":Number(t).toFixed(e)}function yt(t){const e=t.trim();return e?JSON.parse(e):null}function C(t,e){t.textContent=typeof e=="string"?e:JSON.stringify(e,null,2)}function Q(t,e){h.messages.push({role:t,content:e,time:new Date().toLocaleTimeString("zh-CN",{hour12:!1})}),G()}function G(){const t=c("#messageList"),e=[...h.messages];if(h.streamingAnswer&&e.push({role:"agent",content:h.streamingAnswer,time:"生成中",streaming:!0}),!e.length){t.innerHTML='<div class="empty-chat">发送一条消息后，聊天记录会显示在这里。</div>';return}t.innerHTML=e.map(r=>`
        <article class="message-card ${r.role} ${r.streaming?"streaming":""}">
          <header>
            <strong>${r.role==="user"?"User":"Agent"}</strong>
            <span>${r.time}</span>
          </header>
          <div class="message-body ${r.role==="agent"?"markdown-body":""}">${r.role==="agent"?k.parse(r.content||""):Pe(r.content).replace(/\n/g,"<br/>")}</div>
        </article>
      `).join(""),t.scrollTop=t.scrollHeight}function Pe(t){return t.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}function St(t){const e=t.trim();return e?/^(🧭|🛠️|✅|🔍|📎|💡|⚙️|🚦|📌|🔀|🧠|\[[^\]]+\])/.test(e):!1}function ze(t){const e=t.split(`
`),r=[],s=[];for(const n of e){if(St(n)){r.push(n.trim());continue}s.push(n)}return{trace:r,answer:s.join(`
`).trim()}}function V(t){const e=c("#traceList");if(!t.length){e.innerHTML='<div class="empty-chat">等待后端返回执行过程...</div>';return}e.innerHTML=t.map((r,s)=>`
        <div class="trace-item">
          <span class="trace-step">${s+1}</span>
          <div>${Pe(r)}</div>
        </div>
      `).join("")}function Y(){h.statusTimer&&(clearInterval(h.statusTimer),h.statusTimer=null)}function $t(){Y(),h.requestStartedAt=Date.now();const t=c("#agentStatus");t.textContent="Agent 正在接收请求...",h.statusTimer=setInterval(()=>{const e=Math.round((Date.now()-h.requestStartedAt)/1e3),r=h.activeTrace[h.activeTrace.length-1];r?t.textContent=`${r} · ${e}s`:t.textContent=`Agent 正在规划 / 检索 / 生成... · ${e}s`},400)}function Rt(){const t=c("#benchmarkHighlights"),e=h.latestBenchmarkMetrics,r=[{label:"复杂任务时延",value:e?`${M(e.complex_request_latency_ms,2)} ms`:"待运行",tone:"dark"}];t.innerHTML=r.map(s=>`
        <div class="metric metric-${s.tone}">
          <span>${s.label}</span>
          <strong>${s.value}</strong>
        </div>
      `).join("")}function Tt(){const t=c("#metricCards"),e=h.latestRetrievalMetrics,r=h.latestBenchmarkMetrics,s=[["Precision@K",e?.avg_precision_at_k,4],["Recall@K",e?.avg_recall_at_k,4],["MRR",e?.mrr,4],["nDCG@K",e?.ndcg_at_k,4],["Avg Query Latency",e?`${M(e.avg_query_latency_ms,2)} ms`:null,null],["Complex Latency",r?`${M(r.complex_request_latency_ms,2)} ms`:null,null]];t.innerHTML=s.map(([n,l,a])=>{const o=typeof l=="string"?l:l==null?"待运行":M(l,a||4);return`
        <div class="stat-card">
          <span>${n}</span>
          <strong>${o}</strong>
        </div>
      `}).join("")}function O(t,e,r,s="",n=4){const l=r>0?Math.max(e/r*100,4):0,a=typeof e=="number"?`${e.toFixed(n)}${s}`:e;return`
    <div class="bar-row">
      <div class="bar-meta">
        <strong>${t}</strong>
        <span>${a}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${l}%"></div>
      </div>
    </div>
  `}function Ct(){const t=c("#compareChart"),e=h.latestCompareReport;if(!e?.baselines?.length){t.className="chart-panel empty-state",t.textContent="运行 Baseline Compare 后显示";return}const r=Math.max(...e.baselines.map(l=>l.avg_recall_at_k),1),s=Math.max(...e.baselines.map(l=>l.mrr),1),n=Math.max(...e.baselines.map(l=>l.avg_query_latency_ms),1);t.className="chart-panel",t.innerHTML=e.baselines.map(l=>`
        <section class="compare-card">
          <h5>${l.strategy}</h5>
          ${O("Recall",l.avg_recall_at_k,r)}
          ${O("MRR",l.mrr,s)}
          ${O("Latency",l.avg_query_latency_ms,n," ms",2)}
        </section>
      `).join("")}function _t(){const t=c("#benchmarkChart"),e=h.latestBenchmarkMetrics;if(!e){t.className="chart-panel empty-state",t.textContent="运行 System Benchmark 后显示";return}const r=[["Retrieval Avg",e.retrieval_avg_latency_ms],["Retrieval P95",e.retrieval_p95_latency_ms],["Simple Request",e.simple_request_latency_ms],["Complex Request",e.complex_request_latency_ms]],s=Math.max(...r.map(([,n])=>n),1);t.className="chart-panel benchmark-layout",t.innerHTML=r.map(([n,l])=>O(n,l,s," ms",2)).join("")}function z(){Rt(),Tt(),Ct(),_t()}async function At(t,e){if(!t.body)throw new Error("stream body not available");const r=t.body.getReader(),s=new TextDecoder("utf-8");let n="";for(;;){const{done:l,value:a}=await r.read();if(l)break;n+=s.decode(a,{stream:!0}),e.textContent=n,e.scrollTop=e.scrollHeight;const o=ze(n);h.activeTrace=o.trace,h.streamingAnswer=o.answer,V(o.trace),G()}return n}async function I(t,e={}){const r=await fetch(`${h.apiBase}${t}`,{headers:{"Content-Type":"application/json",...e.headers||{}},...e});if(!r.ok){const s=await r.text();throw new Error(s||`request failed: ${r.status}`)}return r.json()}ve.addEventListener("change",()=>{h.apiBase=ve.value.trim()||"/api/v1",localStorage.setItem("agent-api-base",h.apiBase)});X.addEventListener("change",()=>{h.threadId=X.value.trim(),localStorage.setItem("agent-thread-id",h.threadId)});c("#regenThread").addEventListener("click",()=>{h.threadId=Be(),X.value=h.threadId,localStorage.setItem("agent-thread-id",h.threadId)});c("#clearChat").addEventListener("click",()=>{h.messages=[],h.activeTrace=[],h.streamingAnswer="",c("#traceList").innerHTML='<div class="empty-chat">会话已清空。</div>',c("#agentStatus").textContent="会话已清空。",G()});async function Ie(){const t=c("#query"),e=t.value.trim();if(!e){c("#agentStatus").textContent="请输入问题。";return}h.activeTrace=[],h.streamingAnswer="",V([]),$t(),Q("user",e),t.value="";try{const r=yt(c("#metadataFilters").value),s=await fetch(`${h.apiBase}/chat/agent`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,thread_id:h.threadId,user_id:c("#userId").value.trim(),task_mode:null,metadata_filters:r})});if(!s.ok)throw new Error(await s.text());const n=document.createElement("pre"),l=await At(s,n),a=ze(l);V(a.trace),h.streamingAnswer="",c("#agentStatus").textContent="生成完成",Q("agent",a.answer||l||"空响应"),Y()}catch(r){Y(),h.streamingAnswer="",c("#agentStatus").textContent=`请求失败：${r.message}`,Q("agent",`请求失败：${r.message}`)}}c("#sendChat").addEventListener("click",Ie);c("#openRail").addEventListener("click",()=>ce(!h.railOpen));c("#closeRail").addEventListener("click",()=>ce(!1));c("#query").addEventListener("keydown",t=>{t.key==="Enter"&&!t.shiftKey&&(t.preventDefault(),Ie())});c("#uploadKnowledge").addEventListener("click",async()=>{const t=c("#knowledgeFile").files[0],e=c("#uploadResult");if(!t){e.textContent="请先选择文件。";return}try{const r=new FormData;r.append("file",t);const n=await(await fetch(`${h.apiBase}/knowledge/upload`,{method:"POST",body:r})).json();C(e,n)}catch(r){e.textContent=`上传失败：${r.message}`}});c("#rebuildEnv").addEventListener("click",async()=>{const t=c("#rebuildResult");T("showTestingPanel"),c("#evalStatus").textContent="正在重建测试环境...",t.textContent="正在重建测试环境...";try{const e=await I("/testing/rebuild",{method:"POST",body:JSON.stringify({force_download:c("#forceDownload").checked,run_retrieval_eval:c("#runRetrievalEvalAfterRebuild").checked})});C(t,e),e?.result?.retrieval_eval&&(h.latestRetrievalMetrics=e.result.retrieval_eval,z()),c("#evalStatus").textContent="测试环境重建完成。"}catch(e){t.textContent=`重建失败：${e.message}`,c("#evalStatus").textContent=`测试环境重建失败：${e.message}`}});c("#runRetrievalEval").addEventListener("click",async()=>{const t=c("#retrievalEvalResult");T("runRetrievalEval"),c("#evalStatus").textContent="正在运行 Retrieval Eval...",t.textContent="正在运行 retrieval eval...";try{const e=await I("/eval/retrieval",{method:"POST",body:JSON.stringify({top_k:Number(c("#topK").value),candidate_k:Number(c("#candidateK").value),strategy:c("#strategy").value})});C(t,e),h.latestRetrievalMetrics=e.metrics,z(),c("#evalStatus").textContent="Retrieval Eval 运行完成。"}catch(e){t.textContent=`retrieval eval 失败：${e.message}`,c("#evalStatus").textContent=`Retrieval Eval 失败：${e.message}`}});c("#runCompare").addEventListener("click",async()=>{const t=c("#compareResult");T("runCompare"),c("#evalStatus").textContent="正在运行 Baseline Compare...",t.textContent="正在运行 baseline compare...";try{const e=await I("/eval/retrieval/compare",{method:"POST",body:JSON.stringify({top_k:Number(c("#topK").value),candidate_k:Number(c("#candidateK").value),strategy:c("#strategy").value})});C(t,e),h.latestCompareReport=e.report;const r=e.report?.baselines?.find(s=>s.strategy===c("#strategy").value)||e.report?.baselines?.[e.report?.baselines?.length-1];r&&(h.latestRetrievalMetrics=r),z(),c("#evalStatus").textContent="Baseline Compare 运行完成。"}catch(e){t.textContent=`compare 失败：${e.message}`,c("#evalStatus").textContent=`Baseline Compare 失败：${e.message}`}});c("#runGenerationEval").addEventListener("click",async()=>{const t=c("#generationEvalResult");T("runGenerationEval"),c("#evalStatus").textContent="正在运行 Generation Eval...",t.textContent="正在运行 generation eval...";try{const e=await I("/eval/generation",{method:"POST",body:JSON.stringify({candidate_k:Number(c("#candidateK").value)})});C(t,e),c("#evalStatus").textContent="Generation Eval 运行完成。"}catch(e){t.textContent=`generation eval 失败：${e.message}`,c("#evalStatus").textContent=`Generation Eval 失败：${e.message}`}});c("#runBenchmark").addEventListener("click",async()=>{const t=c("#benchmarkResult");T("runBenchmark"),c("#evalStatus").textContent="正在运行 System Benchmark...",t.textContent="正在运行 system benchmark...";try{const e=await I("/eval/benchmark",{method:"POST",body:JSON.stringify({candidate_k:Number(c("#candidateK").value)})});C(t,e),h.latestBenchmarkMetrics=e.metrics,z(),c("#evalStatus").textContent="System Benchmark 运行完成。"}catch(e){t.textContent=`benchmark 失败：${e.message}`,c("#evalStatus").textContent=`System Benchmark 失败：${e.message}`}});c("#showTestingPanel").addEventListener("click",()=>{T("showTestingPanel"),c("#evalStatus").textContent="当前显示测试环境重建模块。"});G();z();ce(!1);T(null);
