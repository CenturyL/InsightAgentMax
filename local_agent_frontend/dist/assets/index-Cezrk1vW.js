(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const t of document.querySelectorAll('link[rel="modulepreload"]'))s(t);new MutationObserver(t=>{for(const l of t)if(l.type==="childList")for(const a of l.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&s(a)}).observe(document,{childList:!0,subtree:!0});function n(t){const l={};return t.integrity&&(l.integrity=t.integrity),t.referrerPolicy&&(l.referrerPolicy=t.referrerPolicy),t.crossOrigin==="use-credentials"?l.credentials="include":t.crossOrigin==="anonymous"?l.credentials="omit":l.credentials="same-origin",l}function s(t){if(t.ep)return;t.ep=!0;const l=n(t);fetch(t.href,l)}})();function ee(){return{async:!1,breaks:!1,extensions:null,gfm:!0,hooks:null,pedantic:!1,renderer:null,silent:!1,tokenizer:null,walkTokens:null}}var R=ee();function we(r){R=r}var P={exec:()=>null};function d(r,e=""){let n=typeof r=="string"?r:r.source,s={replace:(t,l)=>{let a=typeof l=="string"?l:l.source;return a=a.replace(x.caret,"$1"),n=n.replace(t,a),s},getRegex:()=>new RegExp(n,e)};return s}var Me=(()=>{try{return!!new RegExp("(?<=1)(?<!1)")}catch{return!1}})(),x={codeRemoveIndent:/^(?: {1,4}| {0,3}\t)/gm,outputLinkReplace:/\\([\[\]])/g,indentCodeCompensation:/^(\s+)(?:```)/,beginningSpace:/^\s+/,endingHash:/#$/,startingSpaceChar:/^ /,endingSpaceChar:/ $/,nonSpaceChar:/[^ ]/,newLineCharGlobal:/\n/g,tabCharGlobal:/\t/g,multipleSpaceGlobal:/\s+/g,blankLine:/^[ \t]*$/,doubleBlankLine:/\n[ \t]*\n[ \t]*$/,blockquoteStart:/^ {0,3}>/,blockquoteSetextReplace:/\n {0,3}((?:=+|-+) *)(?=\n|$)/g,blockquoteSetextReplace2:/^ {0,3}>[ \t]?/gm,listReplaceTabs:/^\t+/,listReplaceNesting:/^ {1,4}(?=( {4})*[^ ])/g,listIsTask:/^\[[ xX]\] /,listReplaceTask:/^\[[ xX]\] +/,anyLine:/\n.*\n/,hrefBrackets:/^<(.*)>$/,tableDelimiter:/[:|]/,tableAlignChars:/^\||\| *$/g,tableRowBlankLine:/\n[ \t]*$/,tableAlignRight:/^ *-+: *$/,tableAlignCenter:/^ *:-+: *$/,tableAlignLeft:/^ *:-+ *$/,startATag:/^<a /i,endATag:/^<\/a>/i,startPreScriptTag:/^<(pre|code|kbd|script)(\s|>)/i,endPreScriptTag:/^<\/(pre|code|kbd|script)(\s|>)/i,startAngleBracket:/^</,endAngleBracket:/>$/,pedanticHrefTitle:/^([^'"]*[^\s])\s+(['"])(.*)\2/,unicodeAlphaNumeric:/[\p{L}\p{N}]/u,escapeTest:/[&<>"']/,escapeReplace:/[&<>"']/g,escapeTestNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/,escapeReplaceNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/g,unescapeTest:/&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig,caret:/(^|[^\[])\^/g,percentDecode:/%25/g,findPipe:/\|/g,splitPipe:/ \|/,slashPipe:/\\\|/g,carriageReturn:/\r\n|\r/g,spaceLine:/^ +$/gm,notSpaceStart:/^\S*/,endingNewline:/\n$/,listItemRegex:r=>new RegExp(`^( {0,3}${r})((?:[	 ][^\\n]*)?(?:\\n|$))`),nextBulletRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`),hrRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`),fencesBeginRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}(?:\`\`\`|~~~)`),headingBeginRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}#`),htmlBeginRegex:r=>new RegExp(`^ {0,${Math.min(3,r-1)}}<(?:[a-z].*>|!--)`,"i")},Oe=/^(?:[ \t]*(?:\n|$))+/,Ne=/^((?: {4}| {0,3}\t)[^\n]+(?:\n(?:[ \t]*(?:\n|$))*)?)+/,He=/^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/,z=/^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/,De=/^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/,te=/(?:[*+-]|\d{1,9}[.)])/,ye=/^(?!bull |blockCode|fences|blockquote|heading|html|table)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html|table))+?)\n {0,3}(=+|-+) *(?:\n+|$)/,Se=d(ye).replace(/bull/g,te).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/\|table/g,"").getRegex(),je=d(ye).replace(/bull/g,te).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/table/g,/ {0,3}\|?(?:[:\- ]*\|)+[\:\- ]*\n/).getRegex(),re=/^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/,Ze=/^[^\n]+/,ne=/(?!\s*\])(?:\\[\s\S]|[^\[\]\\])+/,Ge=d(/^ {0,3}\[(label)\]: *(?:\n[ \t]*)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n[ \t]*)?| *\n[ \t]*)(title))? *(?:\n+|$)/).replace("label",ne).replace("title",/(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(),Ke=d(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g,te).getRegex(),j="address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul",se=/<!--(?:-?>|[\s\S]*?(?:-->|$))/,Fe=d("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$))","i").replace("comment",se).replace("tag",j).replace("attribute",/ +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(),$e=d(re).replace("hr",z).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("|table","").replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",j).getRegex(),Qe=d(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph",$e).getRegex(),ae={blockquote:Qe,code:Ne,def:Ge,fences:He,heading:De,hr:z,html:Fe,lheading:Se,list:Ke,newline:Oe,paragraph:$e,table:P,text:Ze},ge=d("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr",z).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("blockquote"," {0,3}>").replace("code","(?: {4}| {0,3}	)[^\\n]").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",j).getRegex(),Je={...ae,lheading:je,table:ge,paragraph:d(re).replace("hr",z).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("table",ge).replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)]) ").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",j).getRegex()},Ue={...ae,html:d(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment",se).replace(/tag/g,"(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),def:/^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,heading:/^(#{1,6})(.*)(?:\n+|$)/,fences:P,lheading:/^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,paragraph:d(re).replace("hr",z).replace("heading",` *#{1,6} *[^
]`).replace("lheading",Se).replace("|table","").replace("blockquote"," {0,3}>").replace("|fences","").replace("|list","").replace("|html","").replace("|tag","").getRegex()},We=/^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/,Xe=/^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/,Re=/^( {2,}|\\)\n(?!\s*$)/,Ve=/^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/,Z=/[\p{P}\p{S}]/u,le=/[\s\p{P}\p{S}]/u,Te=/[^\s\p{P}\p{S}]/u,Ye=d(/^((?![*_])punctSpace)/,"u").replace(/punctSpace/g,le).getRegex(),Ce=/(?!~)[\p{P}\p{S}]/u,et=/(?!~)[\s\p{P}\p{S}]/u,tt=/(?:[^\s\p{P}\p{S}]|~)/u,rt=d(/link|precode-code|html/,"g").replace("link",/\[(?:[^\[\]`]|(?<a>`+)[^`]+\k<a>(?!`))*?\]\((?:\\[\s\S]|[^\\\(\)]|\((?:\\[\s\S]|[^\\\(\)])*\))*\)/).replace("precode-",Me?"(?<!`)()":"(^^|[^`])").replace("code",/(?<b>`+)[^`]+\k<b>(?!`)/).replace("html",/<(?! )[^<>]*?>/).getRegex(),_e=/^(?:\*+(?:((?!\*)punct)|[^\s*]))|^_+(?:((?!_)punct)|([^\s_]))/,nt=d(_e,"u").replace(/punct/g,Z).getRegex(),st=d(_e,"u").replace(/punct/g,Ce).getRegex(),Ae="^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)punct(\\*+)(?=[\\s]|$)|notPunctSpace(\\*+)(?!\\*)(?=punctSpace|$)|(?!\\*)punctSpace(\\*+)(?=notPunctSpace)|[\\s](\\*+)(?!\\*)(?=punct)|(?!\\*)punct(\\*+)(?!\\*)(?=punct)|notPunctSpace(\\*+)(?=notPunctSpace)",at=d(Ae,"gu").replace(/notPunctSpace/g,Te).replace(/punctSpace/g,le).replace(/punct/g,Z).getRegex(),lt=d(Ae,"gu").replace(/notPunctSpace/g,tt).replace(/punctSpace/g,et).replace(/punct/g,Ce).getRegex(),it=d("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)punct(_+)(?=[\\s]|$)|notPunctSpace(_+)(?!_)(?=punctSpace|$)|(?!_)punctSpace(_+)(?=notPunctSpace)|[\\s](_+)(?!_)(?=punct)|(?!_)punct(_+)(?!_)(?=punct)","gu").replace(/notPunctSpace/g,Te).replace(/punctSpace/g,le).replace(/punct/g,Z).getRegex(),ot=d(/\\(punct)/,"gu").replace(/punct/g,Z).getRegex(),ct=d(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme",/[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email",/[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(),pt=d(se).replace("(?:-->|$)","-->").getRegex(),ht=d("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment",pt).replace("attribute",/\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(),N=/(?:\[(?:\\[\s\S]|[^\[\]\\])*\]|\\[\s\S]|`+[^`]*?`+(?!`)|[^\[\]\\`])*?/,ut=d(/^!?\[(label)\]\(\s*(href)(?:(?:[ \t]*(?:\n[ \t]*)?)(title))?\s*\)/).replace("label",N).replace("href",/<(?:\\.|[^\n<>\\])+>|[^ \t\n\x00-\x1f]*/).replace("title",/"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(),Ee=d(/^!?\[(label)\]\[(ref)\]/).replace("label",N).replace("ref",ne).getRegex(),Le=d(/^!?\[(ref)\](?:\[\])?/).replace("ref",ne).getRegex(),dt=d("reflink|nolink(?!\\()","g").replace("reflink",Ee).replace("nolink",Le).getRegex(),ke=/[hH][tT][tT][pP][sS]?|[fF][tT][pP]/,ie={_backpedal:P,anyPunctuation:ot,autolink:ct,blockSkip:rt,br:Re,code:Xe,del:P,emStrongLDelim:nt,emStrongRDelimAst:at,emStrongRDelimUnd:it,escape:We,link:ut,nolink:Le,punctuation:Ye,reflink:Ee,reflinkSearch:dt,tag:ht,text:Ve,url:P},gt={...ie,link:d(/^!?\[(label)\]\((.*?)\)/).replace("label",N).getRegex(),reflink:d(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label",N).getRegex()},J={...ie,emStrongRDelimAst:lt,emStrongLDelim:st,url:d(/^((?:protocol):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/).replace("protocol",ke).replace("email",/[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),_backpedal:/(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,del:/^(~~?)(?=[^\s~])((?:\\[\s\S]|[^\\])*?(?:\\[\s\S]|[^\s~\\]))\1(?=[^~]|$)/,text:d(/^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|protocol:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/).replace("protocol",ke).getRegex()},kt={...J,br:d(Re).replace("{2,}","*").getRegex(),text:d(J.text).replace("\\b_","\\b_| {2,}\\n").replace(/\{2,\}/g,"*").getRegex()},M={normal:ae,gfm:Je,pedantic:Ue},E={normal:ie,gfm:J,breaks:kt,pedantic:gt},ft={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"},fe=r=>ft[r];function S(r,e){if(e){if(x.escapeTest.test(r))return r.replace(x.escapeReplace,fe)}else if(x.escapeTestNoEncode.test(r))return r.replace(x.escapeReplaceNoEncode,fe);return r}function me(r){try{r=encodeURI(r).replace(x.percentDecode,"%")}catch{return null}return r}function be(r,e){let n=r.replace(x.findPipe,(l,a,o)=>{let i=!1,u=a;for(;--u>=0&&o[u]==="\\";)i=!i;return i?"|":" |"}),s=n.split(x.splitPipe),t=0;if(s[0].trim()||s.shift(),s.length>0&&!s.at(-1)?.trim()&&s.pop(),e)if(s.length>e)s.splice(e);else for(;s.length<e;)s.push("");for(;t<s.length;t++)s[t]=s[t].trim().replace(x.slashPipe,"|");return s}function L(r,e,n){let s=r.length;if(s===0)return"";let t=0;for(;t<s&&r.charAt(s-t-1)===e;)t++;return r.slice(0,s-t)}function mt(r,e){if(r.indexOf(e[1])===-1)return-1;let n=0;for(let s=0;s<r.length;s++)if(r[s]==="\\")s++;else if(r[s]===e[0])n++;else if(r[s]===e[1]&&(n--,n<0))return s;return n>0?-2:-1}function xe(r,e,n,s,t){let l=e.href,a=e.title||null,o=r[1].replace(t.other.outputLinkReplace,"$1");s.state.inLink=!0;let i={type:r[0].charAt(0)==="!"?"image":"link",raw:n,href:l,title:a,text:o,tokens:s.inlineTokens(o)};return s.state.inLink=!1,i}function bt(r,e,n){let s=r.match(n.other.indentCodeCompensation);if(s===null)return e;let t=s[1];return e.split(`
`).map(l=>{let a=l.match(n.other.beginningSpace);if(a===null)return l;let[o]=a;return o.length>=t.length?l.slice(t.length):l}).join(`
`)}var H=class{options;rules;lexer;constructor(r){this.options=r||R}space(r){let e=this.rules.block.newline.exec(r);if(e&&e[0].length>0)return{type:"space",raw:e[0]}}code(r){let e=this.rules.block.code.exec(r);if(e){let n=e[0].replace(this.rules.other.codeRemoveIndent,"");return{type:"code",raw:e[0],codeBlockStyle:"indented",text:this.options.pedantic?n:L(n,`
`)}}}fences(r){let e=this.rules.block.fences.exec(r);if(e){let n=e[0],s=bt(n,e[3]||"",this.rules);return{type:"code",raw:n,lang:e[2]?e[2].trim().replace(this.rules.inline.anyPunctuation,"$1"):e[2],text:s}}}heading(r){let e=this.rules.block.heading.exec(r);if(e){let n=e[2].trim();if(this.rules.other.endingHash.test(n)){let s=L(n,"#");(this.options.pedantic||!s||this.rules.other.endingSpaceChar.test(s))&&(n=s.trim())}return{type:"heading",raw:e[0],depth:e[1].length,text:n,tokens:this.lexer.inline(n)}}}hr(r){let e=this.rules.block.hr.exec(r);if(e)return{type:"hr",raw:L(e[0],`
`)}}blockquote(r){let e=this.rules.block.blockquote.exec(r);if(e){let n=L(e[0],`
`).split(`
`),s="",t="",l=[];for(;n.length>0;){let a=!1,o=[],i;for(i=0;i<n.length;i++)if(this.rules.other.blockquoteStart.test(n[i]))o.push(n[i]),a=!0;else if(!a)o.push(n[i]);else break;n=n.slice(i);let u=o.join(`
`),p=u.replace(this.rules.other.blockquoteSetextReplace,`
    $1`).replace(this.rules.other.blockquoteSetextReplace2,"");s=s?`${s}
${u}`:u,t=t?`${t}
${p}`:p;let f=this.lexer.state.top;if(this.lexer.state.top=!0,this.lexer.blockTokens(p,l,!0),this.lexer.state.top=f,n.length===0)break;let g=l.at(-1);if(g?.type==="code")break;if(g?.type==="blockquote"){let b=g,m=b.raw+`
`+n.join(`
`),v=this.blockquote(m);l[l.length-1]=v,s=s.substring(0,s.length-b.raw.length)+v.raw,t=t.substring(0,t.length-b.text.length)+v.text;break}else if(g?.type==="list"){let b=g,m=b.raw+`
`+n.join(`
`),v=this.list(m);l[l.length-1]=v,s=s.substring(0,s.length-g.raw.length)+v.raw,t=t.substring(0,t.length-b.raw.length)+v.raw,n=m.substring(l.at(-1).raw.length).split(`
`);continue}}return{type:"blockquote",raw:s,tokens:l,text:t}}}list(r){let e=this.rules.block.list.exec(r);if(e){let n=e[1].trim(),s=n.length>1,t={type:"list",raw:"",ordered:s,start:s?+n.slice(0,-1):"",loose:!1,items:[]};n=s?`\\d{1,9}\\${n.slice(-1)}`:`\\${n}`,this.options.pedantic&&(n=s?n:"[*+-]");let l=this.rules.other.listItemRegex(n),a=!1;for(;r;){let i=!1,u="",p="";if(!(e=l.exec(r))||this.rules.block.hr.test(r))break;u=e[0],r=r.substring(u.length);let f=e[2].split(`
`,1)[0].replace(this.rules.other.listReplaceTabs,K=>" ".repeat(3*K.length)),g=r.split(`
`,1)[0],b=!f.trim(),m=0;if(this.options.pedantic?(m=2,p=f.trimStart()):b?m=e[1].length+1:(m=e[2].search(this.rules.other.nonSpaceChar),m=m>4?1:m,p=f.slice(m),m+=e[1].length),b&&this.rules.other.blankLine.test(g)&&(u+=g+`
`,r=r.substring(g.length+1),i=!0),!i){let K=this.rules.other.nextBulletRegex(m),he=this.rules.other.hrRegex(m),ue=this.rules.other.fencesBeginRegex(m),de=this.rules.other.headingBeginRegex(m),qe=this.rules.other.htmlBeginRegex(m);for(;r;){let F=r.split(`
`,1)[0],A;if(g=F,this.options.pedantic?(g=g.replace(this.rules.other.listReplaceNesting,"  "),A=g):A=g.replace(this.rules.other.tabCharGlobal,"    "),ue.test(g)||de.test(g)||qe.test(g)||K.test(g)||he.test(g))break;if(A.search(this.rules.other.nonSpaceChar)>=m||!g.trim())p+=`
`+A.slice(m);else{if(b||f.replace(this.rules.other.tabCharGlobal,"    ").search(this.rules.other.nonSpaceChar)>=4||ue.test(f)||de.test(f)||he.test(f))break;p+=`
`+g}!b&&!g.trim()&&(b=!0),u+=F+`
`,r=r.substring(F.length+1),f=A.slice(m)}}t.loose||(a?t.loose=!0:this.rules.other.doubleBlankLine.test(u)&&(a=!0));let v=null,pe;this.options.gfm&&(v=this.rules.other.listIsTask.exec(p),v&&(pe=v[0]!=="[ ] ",p=p.replace(this.rules.other.listReplaceTask,""))),t.items.push({type:"list_item",raw:u,task:!!v,checked:pe,loose:!1,text:p,tokens:[]}),t.raw+=u}let o=t.items.at(-1);if(o)o.raw=o.raw.trimEnd(),o.text=o.text.trimEnd();else return;t.raw=t.raw.trimEnd();for(let i=0;i<t.items.length;i++)if(this.lexer.state.top=!1,t.items[i].tokens=this.lexer.blockTokens(t.items[i].text,[]),!t.loose){let u=t.items[i].tokens.filter(f=>f.type==="space"),p=u.length>0&&u.some(f=>this.rules.other.anyLine.test(f.raw));t.loose=p}if(t.loose)for(let i=0;i<t.items.length;i++)t.items[i].loose=!0;return t}}html(r){let e=this.rules.block.html.exec(r);if(e)return{type:"html",block:!0,raw:e[0],pre:e[1]==="pre"||e[1]==="script"||e[1]==="style",text:e[0]}}def(r){let e=this.rules.block.def.exec(r);if(e){let n=e[1].toLowerCase().replace(this.rules.other.multipleSpaceGlobal," "),s=e[2]?e[2].replace(this.rules.other.hrefBrackets,"$1").replace(this.rules.inline.anyPunctuation,"$1"):"",t=e[3]?e[3].substring(1,e[3].length-1).replace(this.rules.inline.anyPunctuation,"$1"):e[3];return{type:"def",tag:n,raw:e[0],href:s,title:t}}}table(r){let e=this.rules.block.table.exec(r);if(!e||!this.rules.other.tableDelimiter.test(e[2]))return;let n=be(e[1]),s=e[2].replace(this.rules.other.tableAlignChars,"").split("|"),t=e[3]?.trim()?e[3].replace(this.rules.other.tableRowBlankLine,"").split(`
`):[],l={type:"table",raw:e[0],header:[],align:[],rows:[]};if(n.length===s.length){for(let a of s)this.rules.other.tableAlignRight.test(a)?l.align.push("right"):this.rules.other.tableAlignCenter.test(a)?l.align.push("center"):this.rules.other.tableAlignLeft.test(a)?l.align.push("left"):l.align.push(null);for(let a=0;a<n.length;a++)l.header.push({text:n[a],tokens:this.lexer.inline(n[a]),header:!0,align:l.align[a]});for(let a of t)l.rows.push(be(a,l.header.length).map((o,i)=>({text:o,tokens:this.lexer.inline(o),header:!1,align:l.align[i]})));return l}}lheading(r){let e=this.rules.block.lheading.exec(r);if(e)return{type:"heading",raw:e[0],depth:e[2].charAt(0)==="="?1:2,text:e[1],tokens:this.lexer.inline(e[1])}}paragraph(r){let e=this.rules.block.paragraph.exec(r);if(e){let n=e[1].charAt(e[1].length-1)===`
`?e[1].slice(0,-1):e[1];return{type:"paragraph",raw:e[0],text:n,tokens:this.lexer.inline(n)}}}text(r){let e=this.rules.block.text.exec(r);if(e)return{type:"text",raw:e[0],text:e[0],tokens:this.lexer.inline(e[0])}}escape(r){let e=this.rules.inline.escape.exec(r);if(e)return{type:"escape",raw:e[0],text:e[1]}}tag(r){let e=this.rules.inline.tag.exec(r);if(e)return!this.lexer.state.inLink&&this.rules.other.startATag.test(e[0])?this.lexer.state.inLink=!0:this.lexer.state.inLink&&this.rules.other.endATag.test(e[0])&&(this.lexer.state.inLink=!1),!this.lexer.state.inRawBlock&&this.rules.other.startPreScriptTag.test(e[0])?this.lexer.state.inRawBlock=!0:this.lexer.state.inRawBlock&&this.rules.other.endPreScriptTag.test(e[0])&&(this.lexer.state.inRawBlock=!1),{type:"html",raw:e[0],inLink:this.lexer.state.inLink,inRawBlock:this.lexer.state.inRawBlock,block:!1,text:e[0]}}link(r){let e=this.rules.inline.link.exec(r);if(e){let n=e[2].trim();if(!this.options.pedantic&&this.rules.other.startAngleBracket.test(n)){if(!this.rules.other.endAngleBracket.test(n))return;let l=L(n.slice(0,-1),"\\");if((n.length-l.length)%2===0)return}else{let l=mt(e[2],"()");if(l===-2)return;if(l>-1){let a=(e[0].indexOf("!")===0?5:4)+e[1].length+l;e[2]=e[2].substring(0,l),e[0]=e[0].substring(0,a).trim(),e[3]=""}}let s=e[2],t="";if(this.options.pedantic){let l=this.rules.other.pedanticHrefTitle.exec(s);l&&(s=l[1],t=l[3])}else t=e[3]?e[3].slice(1,-1):"";return s=s.trim(),this.rules.other.startAngleBracket.test(s)&&(this.options.pedantic&&!this.rules.other.endAngleBracket.test(n)?s=s.slice(1):s=s.slice(1,-1)),xe(e,{href:s&&s.replace(this.rules.inline.anyPunctuation,"$1"),title:t&&t.replace(this.rules.inline.anyPunctuation,"$1")},e[0],this.lexer,this.rules)}}reflink(r,e){let n;if((n=this.rules.inline.reflink.exec(r))||(n=this.rules.inline.nolink.exec(r))){let s=(n[2]||n[1]).replace(this.rules.other.multipleSpaceGlobal," "),t=e[s.toLowerCase()];if(!t){let l=n[0].charAt(0);return{type:"text",raw:l,text:l}}return xe(n,t,n[0],this.lexer,this.rules)}}emStrong(r,e,n=""){let s=this.rules.inline.emStrongLDelim.exec(r);if(!(!s||s[3]&&n.match(this.rules.other.unicodeAlphaNumeric))&&(!(s[1]||s[2])||!n||this.rules.inline.punctuation.exec(n))){let t=[...s[0]].length-1,l,a,o=t,i=0,u=s[0][0]==="*"?this.rules.inline.emStrongRDelimAst:this.rules.inline.emStrongRDelimUnd;for(u.lastIndex=0,e=e.slice(-1*r.length+t);(s=u.exec(e))!=null;){if(l=s[1]||s[2]||s[3]||s[4]||s[5]||s[6],!l)continue;if(a=[...l].length,s[3]||s[4]){o+=a;continue}else if((s[5]||s[6])&&t%3&&!((t+a)%3)){i+=a;continue}if(o-=a,o>0)continue;a=Math.min(a,a+o+i);let p=[...s[0]][0].length,f=r.slice(0,t+s.index+p+a);if(Math.min(t,a)%2){let b=f.slice(1,-1);return{type:"em",raw:f,text:b,tokens:this.lexer.inlineTokens(b)}}let g=f.slice(2,-2);return{type:"strong",raw:f,text:g,tokens:this.lexer.inlineTokens(g)}}}}codespan(r){let e=this.rules.inline.code.exec(r);if(e){let n=e[2].replace(this.rules.other.newLineCharGlobal," "),s=this.rules.other.nonSpaceChar.test(n),t=this.rules.other.startingSpaceChar.test(n)&&this.rules.other.endingSpaceChar.test(n);return s&&t&&(n=n.substring(1,n.length-1)),{type:"codespan",raw:e[0],text:n}}}br(r){let e=this.rules.inline.br.exec(r);if(e)return{type:"br",raw:e[0]}}del(r){let e=this.rules.inline.del.exec(r);if(e)return{type:"del",raw:e[0],text:e[2],tokens:this.lexer.inlineTokens(e[2])}}autolink(r){let e=this.rules.inline.autolink.exec(r);if(e){let n,s;return e[2]==="@"?(n=e[1],s="mailto:"+n):(n=e[1],s=n),{type:"link",raw:e[0],text:n,href:s,tokens:[{type:"text",raw:n,text:n}]}}}url(r){let e;if(e=this.rules.inline.url.exec(r)){let n,s;if(e[2]==="@")n=e[0],s="mailto:"+n;else{let t;do t=e[0],e[0]=this.rules.inline._backpedal.exec(e[0])?.[0]??"";while(t!==e[0]);n=e[0],e[1]==="www."?s="http://"+e[0]:s=e[0]}return{type:"link",raw:e[0],text:n,href:s,tokens:[{type:"text",raw:n,text:n}]}}}inlineText(r){let e=this.rules.inline.text.exec(r);if(e){let n=this.lexer.state.inRawBlock;return{type:"text",raw:e[0],text:e[0],escaped:n}}}},w=class U{tokens;options;state;tokenizer;inlineQueue;constructor(e){this.tokens=[],this.tokens.links=Object.create(null),this.options=e||R,this.options.tokenizer=this.options.tokenizer||new H,this.tokenizer=this.options.tokenizer,this.tokenizer.options=this.options,this.tokenizer.lexer=this,this.inlineQueue=[],this.state={inLink:!1,inRawBlock:!1,top:!0};let n={other:x,block:M.normal,inline:E.normal};this.options.pedantic?(n.block=M.pedantic,n.inline=E.pedantic):this.options.gfm&&(n.block=M.gfm,this.options.breaks?n.inline=E.breaks:n.inline=E.gfm),this.tokenizer.rules=n}static get rules(){return{block:M,inline:E}}static lex(e,n){return new U(n).lex(e)}static lexInline(e,n){return new U(n).inlineTokens(e)}lex(e){e=e.replace(x.carriageReturn,`
`),this.blockTokens(e,this.tokens);for(let n=0;n<this.inlineQueue.length;n++){let s=this.inlineQueue[n];this.inlineTokens(s.src,s.tokens)}return this.inlineQueue=[],this.tokens}blockTokens(e,n=[],s=!1){for(this.options.pedantic&&(e=e.replace(x.tabCharGlobal,"    ").replace(x.spaceLine,""));e;){let t;if(this.options.extensions?.block?.some(a=>(t=a.call({lexer:this},e,n))?(e=e.substring(t.raw.length),n.push(t),!0):!1))continue;if(t=this.tokenizer.space(e)){e=e.substring(t.raw.length);let a=n.at(-1);t.raw.length===1&&a!==void 0?a.raw+=`
`:n.push(t);continue}if(t=this.tokenizer.code(e)){e=e.substring(t.raw.length);let a=n.at(-1);a?.type==="paragraph"||a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.text,this.inlineQueue.at(-1).src=a.text):n.push(t);continue}if(t=this.tokenizer.fences(e)){e=e.substring(t.raw.length),n.push(t);continue}if(t=this.tokenizer.heading(e)){e=e.substring(t.raw.length),n.push(t);continue}if(t=this.tokenizer.hr(e)){e=e.substring(t.raw.length),n.push(t);continue}if(t=this.tokenizer.blockquote(e)){e=e.substring(t.raw.length),n.push(t);continue}if(t=this.tokenizer.list(e)){e=e.substring(t.raw.length),n.push(t);continue}if(t=this.tokenizer.html(e)){e=e.substring(t.raw.length),n.push(t);continue}if(t=this.tokenizer.def(e)){e=e.substring(t.raw.length);let a=n.at(-1);a?.type==="paragraph"||a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.raw,this.inlineQueue.at(-1).src=a.text):this.tokens.links[t.tag]||(this.tokens.links[t.tag]={href:t.href,title:t.title},n.push(t));continue}if(t=this.tokenizer.table(e)){e=e.substring(t.raw.length),n.push(t);continue}if(t=this.tokenizer.lheading(e)){e=e.substring(t.raw.length),n.push(t);continue}let l=e;if(this.options.extensions?.startBlock){let a=1/0,o=e.slice(1),i;this.options.extensions.startBlock.forEach(u=>{i=u.call({lexer:this},o),typeof i=="number"&&i>=0&&(a=Math.min(a,i))}),a<1/0&&a>=0&&(l=e.substring(0,a+1))}if(this.state.top&&(t=this.tokenizer.paragraph(l))){let a=n.at(-1);s&&a?.type==="paragraph"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=a.text):n.push(t),s=l.length!==e.length,e=e.substring(t.raw.length);continue}if(t=this.tokenizer.text(e)){e=e.substring(t.raw.length);let a=n.at(-1);a?.type==="text"?(a.raw+=(a.raw.endsWith(`
`)?"":`
`)+t.raw,a.text+=`
`+t.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=a.text):n.push(t);continue}if(e){let a="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(a);break}else throw new Error(a)}}return this.state.top=!0,n}inline(e,n=[]){return this.inlineQueue.push({src:e,tokens:n}),n}inlineTokens(e,n=[]){let s=e,t=null;if(this.tokens.links){let i=Object.keys(this.tokens.links);if(i.length>0)for(;(t=this.tokenizer.rules.inline.reflinkSearch.exec(s))!=null;)i.includes(t[0].slice(t[0].lastIndexOf("[")+1,-1))&&(s=s.slice(0,t.index)+"["+"a".repeat(t[0].length-2)+"]"+s.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex))}for(;(t=this.tokenizer.rules.inline.anyPunctuation.exec(s))!=null;)s=s.slice(0,t.index)+"++"+s.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);let l;for(;(t=this.tokenizer.rules.inline.blockSkip.exec(s))!=null;)l=t[2]?t[2].length:0,s=s.slice(0,t.index+l)+"["+"a".repeat(t[0].length-l-2)+"]"+s.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);s=this.options.hooks?.emStrongMask?.call({lexer:this},s)??s;let a=!1,o="";for(;e;){a||(o=""),a=!1;let i;if(this.options.extensions?.inline?.some(p=>(i=p.call({lexer:this},e,n))?(e=e.substring(i.raw.length),n.push(i),!0):!1))continue;if(i=this.tokenizer.escape(e)){e=e.substring(i.raw.length),n.push(i);continue}if(i=this.tokenizer.tag(e)){e=e.substring(i.raw.length),n.push(i);continue}if(i=this.tokenizer.link(e)){e=e.substring(i.raw.length),n.push(i);continue}if(i=this.tokenizer.reflink(e,this.tokens.links)){e=e.substring(i.raw.length);let p=n.at(-1);i.type==="text"&&p?.type==="text"?(p.raw+=i.raw,p.text+=i.text):n.push(i);continue}if(i=this.tokenizer.emStrong(e,s,o)){e=e.substring(i.raw.length),n.push(i);continue}if(i=this.tokenizer.codespan(e)){e=e.substring(i.raw.length),n.push(i);continue}if(i=this.tokenizer.br(e)){e=e.substring(i.raw.length),n.push(i);continue}if(i=this.tokenizer.del(e)){e=e.substring(i.raw.length),n.push(i);continue}if(i=this.tokenizer.autolink(e)){e=e.substring(i.raw.length),n.push(i);continue}if(!this.state.inLink&&(i=this.tokenizer.url(e))){e=e.substring(i.raw.length),n.push(i);continue}let u=e;if(this.options.extensions?.startInline){let p=1/0,f=e.slice(1),g;this.options.extensions.startInline.forEach(b=>{g=b.call({lexer:this},f),typeof g=="number"&&g>=0&&(p=Math.min(p,g))}),p<1/0&&p>=0&&(u=e.substring(0,p+1))}if(i=this.tokenizer.inlineText(u)){e=e.substring(i.raw.length),i.raw.slice(-1)!=="_"&&(o=i.raw.slice(-1)),a=!0;let p=n.at(-1);p?.type==="text"?(p.raw+=i.raw,p.text+=i.text):n.push(i);continue}if(e){let p="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(p);break}else throw new Error(p)}}return n}},D=class{options;parser;constructor(r){this.options=r||R}space(r){return""}code({text:r,lang:e,escaped:n}){let s=(e||"").match(x.notSpaceStart)?.[0],t=r.replace(x.endingNewline,"")+`
`;return s?'<pre><code class="language-'+S(s)+'">'+(n?t:S(t,!0))+`</code></pre>
`:"<pre><code>"+(n?t:S(t,!0))+`</code></pre>
`}blockquote({tokens:r}){return`<blockquote>
${this.parser.parse(r)}</blockquote>
`}html({text:r}){return r}def(r){return""}heading({tokens:r,depth:e}){return`<h${e}>${this.parser.parseInline(r)}</h${e}>
`}hr(r){return`<hr>
`}list(r){let e=r.ordered,n=r.start,s="";for(let a=0;a<r.items.length;a++){let o=r.items[a];s+=this.listitem(o)}let t=e?"ol":"ul",l=e&&n!==1?' start="'+n+'"':"";return"<"+t+l+`>
`+s+"</"+t+`>
`}listitem(r){let e="";if(r.task){let n=this.checkbox({checked:!!r.checked});r.loose?r.tokens[0]?.type==="paragraph"?(r.tokens[0].text=n+" "+r.tokens[0].text,r.tokens[0].tokens&&r.tokens[0].tokens.length>0&&r.tokens[0].tokens[0].type==="text"&&(r.tokens[0].tokens[0].text=n+" "+S(r.tokens[0].tokens[0].text),r.tokens[0].tokens[0].escaped=!0)):r.tokens.unshift({type:"text",raw:n+" ",text:n+" ",escaped:!0}):e+=n+" "}return e+=this.parser.parse(r.tokens,!!r.loose),`<li>${e}</li>
`}checkbox({checked:r}){return"<input "+(r?'checked="" ':"")+'disabled="" type="checkbox">'}paragraph({tokens:r}){return`<p>${this.parser.parseInline(r)}</p>
`}table(r){let e="",n="";for(let t=0;t<r.header.length;t++)n+=this.tablecell(r.header[t]);e+=this.tablerow({text:n});let s="";for(let t=0;t<r.rows.length;t++){let l=r.rows[t];n="";for(let a=0;a<l.length;a++)n+=this.tablecell(l[a]);s+=this.tablerow({text:n})}return s&&(s=`<tbody>${s}</tbody>`),`<table>
<thead>
`+e+`</thead>
`+s+`</table>
`}tablerow({text:r}){return`<tr>
${r}</tr>
`}tablecell(r){let e=this.parser.parseInline(r.tokens),n=r.header?"th":"td";return(r.align?`<${n} align="${r.align}">`:`<${n}>`)+e+`</${n}>
`}strong({tokens:r}){return`<strong>${this.parser.parseInline(r)}</strong>`}em({tokens:r}){return`<em>${this.parser.parseInline(r)}</em>`}codespan({text:r}){return`<code>${S(r,!0)}</code>`}br(r){return"<br>"}del({tokens:r}){return`<del>${this.parser.parseInline(r)}</del>`}link({href:r,title:e,tokens:n}){let s=this.parser.parseInline(n),t=me(r);if(t===null)return s;r=t;let l='<a href="'+r+'"';return e&&(l+=' title="'+S(e)+'"'),l+=">"+s+"</a>",l}image({href:r,title:e,text:n,tokens:s}){s&&(n=this.parser.parseInline(s,this.parser.textRenderer));let t=me(r);if(t===null)return S(n);r=t;let l=`<img src="${r}" alt="${n}"`;return e&&(l+=` title="${S(e)}"`),l+=">",l}text(r){return"tokens"in r&&r.tokens?this.parser.parseInline(r.tokens):"escaped"in r&&r.escaped?r.text:S(r.text)}},oe=class{strong({text:e}){return e}em({text:e}){return e}codespan({text:e}){return e}del({text:e}){return e}html({text:e}){return e}text({text:e}){return e}link({text:e}){return""+e}image({text:e}){return""+e}br(){return""}},y=class W{options;renderer;textRenderer;constructor(e){this.options=e||R,this.options.renderer=this.options.renderer||new D,this.renderer=this.options.renderer,this.renderer.options=this.options,this.renderer.parser=this,this.textRenderer=new oe}static parse(e,n){return new W(n).parse(e)}static parseInline(e,n){return new W(n).parseInline(e)}parse(e,n=!0){let s="";for(let t=0;t<e.length;t++){let l=e[t];if(this.options.extensions?.renderers?.[l.type]){let o=l,i=this.options.extensions.renderers[o.type].call({parser:this},o);if(i!==!1||!["space","hr","heading","code","table","blockquote","list","html","def","paragraph","text"].includes(o.type)){s+=i||"";continue}}let a=l;switch(a.type){case"space":{s+=this.renderer.space(a);continue}case"hr":{s+=this.renderer.hr(a);continue}case"heading":{s+=this.renderer.heading(a);continue}case"code":{s+=this.renderer.code(a);continue}case"table":{s+=this.renderer.table(a);continue}case"blockquote":{s+=this.renderer.blockquote(a);continue}case"list":{s+=this.renderer.list(a);continue}case"html":{s+=this.renderer.html(a);continue}case"def":{s+=this.renderer.def(a);continue}case"paragraph":{s+=this.renderer.paragraph(a);continue}case"text":{let o=a,i=this.renderer.text(o);for(;t+1<e.length&&e[t+1].type==="text";)o=e[++t],i+=`
`+this.renderer.text(o);n?s+=this.renderer.paragraph({type:"paragraph",raw:i,text:i,tokens:[{type:"text",raw:i,text:i,escaped:!0}]}):s+=i;continue}default:{let o='Token with "'+a.type+'" type was not found.';if(this.options.silent)return console.error(o),"";throw new Error(o)}}}return s}parseInline(e,n=this.renderer){let s="";for(let t=0;t<e.length;t++){let l=e[t];if(this.options.extensions?.renderers?.[l.type]){let o=this.options.extensions.renderers[l.type].call({parser:this},l);if(o!==!1||!["escape","html","link","image","strong","em","codespan","br","del","text"].includes(l.type)){s+=o||"";continue}}let a=l;switch(a.type){case"escape":{s+=n.text(a);break}case"html":{s+=n.html(a);break}case"link":{s+=n.link(a);break}case"image":{s+=n.image(a);break}case"strong":{s+=n.strong(a);break}case"em":{s+=n.em(a);break}case"codespan":{s+=n.codespan(a);break}case"br":{s+=n.br(a);break}case"del":{s+=n.del(a);break}case"text":{s+=n.text(a);break}default:{let o='Token with "'+a.type+'" type was not found.';if(this.options.silent)return console.error(o),"";throw new Error(o)}}}return s}},B=class{options;block;constructor(r){this.options=r||R}static passThroughHooks=new Set(["preprocess","postprocess","processAllTokens","emStrongMask"]);static passThroughHooksRespectAsync=new Set(["preprocess","postprocess","processAllTokens"]);preprocess(r){return r}postprocess(r){return r}processAllTokens(r){return r}emStrongMask(r){return r}provideLexer(){return this.block?w.lex:w.lexInline}provideParser(){return this.block?y.parse:y.parseInline}},xt=class{defaults=ee();options=this.setOptions;parse=this.parseMarkdown(!0);parseInline=this.parseMarkdown(!1);Parser=y;Renderer=D;TextRenderer=oe;Lexer=w;Tokenizer=H;Hooks=B;constructor(...r){this.use(...r)}walkTokens(r,e){let n=[];for(let s of r)switch(n=n.concat(e.call(this,s)),s.type){case"table":{let t=s;for(let l of t.header)n=n.concat(this.walkTokens(l.tokens,e));for(let l of t.rows)for(let a of l)n=n.concat(this.walkTokens(a.tokens,e));break}case"list":{let t=s;n=n.concat(this.walkTokens(t.items,e));break}default:{let t=s;this.defaults.extensions?.childTokens?.[t.type]?this.defaults.extensions.childTokens[t.type].forEach(l=>{let a=t[l].flat(1/0);n=n.concat(this.walkTokens(a,e))}):t.tokens&&(n=n.concat(this.walkTokens(t.tokens,e)))}}return n}use(...r){let e=this.defaults.extensions||{renderers:{},childTokens:{}};return r.forEach(n=>{let s={...n};if(s.async=this.defaults.async||s.async||!1,n.extensions&&(n.extensions.forEach(t=>{if(!t.name)throw new Error("extension name required");if("renderer"in t){let l=e.renderers[t.name];l?e.renderers[t.name]=function(...a){let o=t.renderer.apply(this,a);return o===!1&&(o=l.apply(this,a)),o}:e.renderers[t.name]=t.renderer}if("tokenizer"in t){if(!t.level||t.level!=="block"&&t.level!=="inline")throw new Error("extension level must be 'block' or 'inline'");let l=e[t.level];l?l.unshift(t.tokenizer):e[t.level]=[t.tokenizer],t.start&&(t.level==="block"?e.startBlock?e.startBlock.push(t.start):e.startBlock=[t.start]:t.level==="inline"&&(e.startInline?e.startInline.push(t.start):e.startInline=[t.start]))}"childTokens"in t&&t.childTokens&&(e.childTokens[t.name]=t.childTokens)}),s.extensions=e),n.renderer){let t=this.defaults.renderer||new D(this.defaults);for(let l in n.renderer){if(!(l in t))throw new Error(`renderer '${l}' does not exist`);if(["options","parser"].includes(l))continue;let a=l,o=n.renderer[a],i=t[a];t[a]=(...u)=>{let p=o.apply(t,u);return p===!1&&(p=i.apply(t,u)),p||""}}s.renderer=t}if(n.tokenizer){let t=this.defaults.tokenizer||new H(this.defaults);for(let l in n.tokenizer){if(!(l in t))throw new Error(`tokenizer '${l}' does not exist`);if(["options","rules","lexer"].includes(l))continue;let a=l,o=n.tokenizer[a],i=t[a];t[a]=(...u)=>{let p=o.apply(t,u);return p===!1&&(p=i.apply(t,u)),p}}s.tokenizer=t}if(n.hooks){let t=this.defaults.hooks||new B;for(let l in n.hooks){if(!(l in t))throw new Error(`hook '${l}' does not exist`);if(["options","block"].includes(l))continue;let a=l,o=n.hooks[a],i=t[a];B.passThroughHooks.has(l)?t[a]=u=>{if(this.defaults.async&&B.passThroughHooksRespectAsync.has(l))return(async()=>{let f=await o.call(t,u);return i.call(t,f)})();let p=o.call(t,u);return i.call(t,p)}:t[a]=(...u)=>{if(this.defaults.async)return(async()=>{let f=await o.apply(t,u);return f===!1&&(f=await i.apply(t,u)),f})();let p=o.apply(t,u);return p===!1&&(p=i.apply(t,u)),p}}s.hooks=t}if(n.walkTokens){let t=this.defaults.walkTokens,l=n.walkTokens;s.walkTokens=function(a){let o=[];return o.push(l.call(this,a)),t&&(o=o.concat(t.call(this,a))),o}}this.defaults={...this.defaults,...s}}),this}setOptions(r){return this.defaults={...this.defaults,...r},this}lexer(r,e){return w.lex(r,e??this.defaults)}parser(r,e){return y.parse(r,e??this.defaults)}parseMarkdown(r){return(e,n)=>{let s={...n},t={...this.defaults,...s},l=this.onError(!!t.silent,!!t.async);if(this.defaults.async===!0&&s.async===!1)return l(new Error("marked(): The async option was set to true by an extension. Remove async: false from the parse options object to return a Promise."));if(typeof e>"u"||e===null)return l(new Error("marked(): input parameter is undefined or null"));if(typeof e!="string")return l(new Error("marked(): input parameter is of type "+Object.prototype.toString.call(e)+", string expected"));if(t.hooks&&(t.hooks.options=t,t.hooks.block=r),t.async)return(async()=>{let a=t.hooks?await t.hooks.preprocess(e):e,o=await(t.hooks?await t.hooks.provideLexer():r?w.lex:w.lexInline)(a,t),i=t.hooks?await t.hooks.processAllTokens(o):o;t.walkTokens&&await Promise.all(this.walkTokens(i,t.walkTokens));let u=await(t.hooks?await t.hooks.provideParser():r?y.parse:y.parseInline)(i,t);return t.hooks?await t.hooks.postprocess(u):u})().catch(l);try{t.hooks&&(e=t.hooks.preprocess(e));let a=(t.hooks?t.hooks.provideLexer():r?w.lex:w.lexInline)(e,t);t.hooks&&(a=t.hooks.processAllTokens(a)),t.walkTokens&&this.walkTokens(a,t.walkTokens);let o=(t.hooks?t.hooks.provideParser():r?y.parse:y.parseInline)(a,t);return t.hooks&&(o=t.hooks.postprocess(o)),o}catch(a){return l(a)}}}onError(r,e){return n=>{if(n.message+=`
Please report this to https://github.com/markedjs/marked.`,r){let s="<p>An error occurred:</p><pre>"+S(n.message+"",!0)+"</pre>";return e?Promise.resolve(s):s}if(e)return Promise.reject(n);throw n}}},$=new xt;function k(r,e){return $.parse(r,e)}k.options=k.setOptions=function(r){return $.setOptions(r),k.defaults=$.defaults,we(k.defaults),k};k.getDefaults=ee;k.defaults=R;k.use=function(...r){return $.use(...r),k.defaults=$.defaults,we(k.defaults),k};k.walkTokens=function(r,e){return $.walkTokens(r,e)};k.parseInline=$.parseInline;k.Parser=y;k.parser=y.parse;k.Renderer=D;k.TextRenderer=oe;k.Lexer=w;k.lexer=w.lex;k.Tokenizer=H;k.Hooks=B;k.parse=k;k.options;k.setOptions;k.use;k.walkTokens;k.parseInline;y.parse;w.lex;function Be(){if(globalThis.crypto?.randomUUID)return globalThis.crypto.randomUUID();const r=Math.random().toString(36).slice(2,10);return`thread-${Date.now()}-${r}`}const vt=Be(),h={apiBase:localStorage.getItem("agent-api-base")||"/api/v1",threadId:localStorage.getItem("agent-thread-id")||vt,messages:[],latestRetrievalMetrics:null,latestCompareReport:null,latestBenchmarkMetrics:null,activeTrace:[],statusTimer:null,requestStartedAt:null,railOpen:!1,activeEvalAction:"runRetrievalEval",streamingAnswer:""};k.setOptions({gfm:!0,breaks:!0});const wt=document.querySelector("#app");wt.innerHTML=`
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

        <section id="retrievalEvalPanel" class="dashboard-card eval-panel">
          <div class="chart-head">
            <div>
              <p class="eyebrow">Metrics</p>
              <h4>Retrieval Eval</h4>
            </div>
          </div>
          <div id="retrievalHighlights" class="hero-metrics hero-metrics-2"></div>
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
`;const c=r=>document.querySelector(r),ve=c("#apiBase"),X=c("#threadId");function ce(r){h.railOpen=r,document.body.dataset.railOpen=r?"true":"false"}function T(r){const e=["runRetrievalEval","runCompare","runGenerationEval","runBenchmark","showTestingPanel"];h.activeEvalAction=r,e.forEach(s=>{const t=c("#"+s);t&&t.classList.toggle("is-active",s===r)});const n={runRetrievalEval:"retrievalEvalPanel",runCompare:"comparePanel",runGenerationEval:"generationEvalPanel",runBenchmark:"benchmarkPanel",showTestingPanel:"testingPanel"};Object.values(n).forEach(s=>{c("#"+s)?.classList.add("hidden")}),c("#"+n[r])?.classList.remove("hidden")}function C(r,e=4){return r==null||Number.isNaN(Number(r))?"-":Number(r).toFixed(e)}function yt(r){const e=r.trim();return e?JSON.parse(e):null}function _(r,e){r.textContent=typeof e=="string"?e:JSON.stringify(e,null,2)}function Q(r,e){h.messages.push({role:r,content:e,time:new Date().toLocaleTimeString("zh-CN",{hour12:!1})}),G()}function G(){const r=c("#messageList"),e=[...h.messages];if(h.streamingAnswer&&e.push({role:"agent",content:h.streamingAnswer,time:"生成中",streaming:!0}),!e.length){r.innerHTML='<div class="empty-chat">发送一条消息后，聊天记录会显示在这里。</div>';return}r.innerHTML=e.map(n=>`
        <article class="message-card ${n.role} ${n.streaming?"streaming":""}">
          <header>
            <strong>${n.role==="user"?"User":"Agent"}</strong>
            <span>${n.time}</span>
          </header>
          <div class="message-body ${n.role==="agent"?"markdown-body":""}">${n.role==="agent"?k.parse(n.content||""):Pe(n.content).replace(/\n/g,"<br/>")}</div>
        </article>
      `).join(""),r.scrollTop=r.scrollHeight}function Pe(r){return r.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}function St(r){const e=r.trim();return e?/^(🧭|🛠️|✅|🔍|📎|💡|⚙️|🚦|📌|🔀|🧠|\[[^\]]+\])/.test(e):!1}function ze(r){const e=r.split(`
`),n=[],s=[];for(const t of e){if(St(t)){n.push(t.trim());continue}s.push(t)}return{trace:n,answer:s.join(`
`).trim()}}function V(r){const e=c("#traceList");if(!r.length){e.innerHTML='<div class="empty-chat">等待后端返回执行过程...</div>';return}e.innerHTML=r.map((n,s)=>`
        <div class="trace-item">
          <span class="trace-step">${s+1}</span>
          <div>${Pe(n)}</div>
        </div>
      `).join("")}function Y(){h.statusTimer&&(clearInterval(h.statusTimer),h.statusTimer=null)}function $t(){Y(),h.requestStartedAt=Date.now();const r=c("#agentStatus");r.textContent="Agent 正在接收请求...",h.statusTimer=setInterval(()=>{const e=Math.round((Date.now()-h.requestStartedAt)/1e3),n=h.activeTrace[h.activeTrace.length-1];n?r.textContent=`${n} · ${e}s`:r.textContent=`Agent 正在规划 / 检索 / 生成... · ${e}s`},400)}function Rt(){const r=c("#retrievalHighlights"),e=c("#benchmarkHighlights"),n=h.latestRetrievalMetrics,s=h.latestBenchmarkMetrics,t=[{label:"最近 Recall@K",value:n?C(n.avg_recall_at_k,4):"待运行",tone:"warm"},{label:"最近 MRR",value:n?C(n.mrr,4):"待运行",tone:"teal"}],l=[{label:"复杂任务时延",value:s?`${C(s.complex_request_latency_ms,2)} ms`:"待运行",tone:"dark"}];r.innerHTML=t.map(a=>`
        <div class="metric metric-${a.tone}">
          <span>${a.label}</span>
          <strong>${a.value}</strong>
        </div>
      `).join(""),e.innerHTML=l.map(a=>`
        <div class="metric metric-${a.tone}">
          <span>${a.label}</span>
          <strong>${a.value}</strong>
        </div>
      `).join("")}function Tt(){const r=c("#metricCards"),e=h.latestRetrievalMetrics,n=h.latestBenchmarkMetrics,s=[["Precision@K",e?.avg_precision_at_k,4],["Recall@K",e?.avg_recall_at_k,4],["MRR",e?.mrr,4],["nDCG@K",e?.ndcg_at_k,4],["Avg Query Latency",e?`${C(e.avg_query_latency_ms,2)} ms`:null,null],["Complex Latency",n?`${C(n.complex_request_latency_ms,2)} ms`:null,null]];r.innerHTML=s.map(([t,l,a])=>{const o=typeof l=="string"?l:l==null?"待运行":C(l,a||4);return`
        <div class="stat-card">
          <span>${t}</span>
          <strong>${o}</strong>
        </div>
      `}).join("")}function O(r,e,n,s="",t=4){const l=n>0?Math.max(e/n*100,4):0,a=typeof e=="number"?`${e.toFixed(t)}${s}`:e;return`
    <div class="bar-row">
      <div class="bar-meta">
        <strong>${r}</strong>
        <span>${a}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${l}%"></div>
      </div>
    </div>
  `}function Ct(){const r=c("#compareChart"),e=h.latestCompareReport;if(!e?.baselines?.length){r.className="chart-panel empty-state",r.textContent="运行 Baseline Compare 后显示";return}const n=Math.max(...e.baselines.map(l=>l.avg_recall_at_k),1),s=Math.max(...e.baselines.map(l=>l.mrr),1),t=Math.max(...e.baselines.map(l=>l.avg_query_latency_ms),1);r.className="chart-panel",r.innerHTML=e.baselines.map(l=>`
        <section class="compare-card">
          <h5>${l.strategy}</h5>
          ${O("Recall",l.avg_recall_at_k,n)}
          ${O("MRR",l.mrr,s)}
          ${O("Latency",l.avg_query_latency_ms,t," ms",2)}
        </section>
      `).join("")}function _t(){const r=c("#benchmarkChart"),e=h.latestBenchmarkMetrics;if(!e){r.className="chart-panel empty-state",r.textContent="运行 System Benchmark 后显示";return}const n=[["Retrieval Avg",e.retrieval_avg_latency_ms],["Retrieval P95",e.retrieval_p95_latency_ms],["Simple Request",e.simple_request_latency_ms],["Complex Request",e.complex_request_latency_ms]],s=Math.max(...n.map(([,t])=>t),1);r.className="chart-panel benchmark-layout",r.innerHTML=n.map(([t,l])=>O(t,l,s," ms",2)).join("")}function I(){Rt(),Tt(),Ct(),_t()}async function At(r,e){if(!r.body)throw new Error("stream body not available");const n=r.body.getReader(),s=new TextDecoder("utf-8");let t="";for(;;){const{done:l,value:a}=await n.read();if(l)break;t+=s.decode(a,{stream:!0}),e.textContent=t,e.scrollTop=e.scrollHeight;const o=ze(t);h.activeTrace=o.trace,h.streamingAnswer=o.answer,V(o.trace),G()}return t}async function q(r,e={}){const n=await fetch(`${h.apiBase}${r}`,{headers:{"Content-Type":"application/json",...e.headers||{}},...e});if(!n.ok){const s=await n.text();throw new Error(s||`request failed: ${n.status}`)}return n.json()}ve.addEventListener("change",()=>{h.apiBase=ve.value.trim()||"/api/v1",localStorage.setItem("agent-api-base",h.apiBase)});X.addEventListener("change",()=>{h.threadId=X.value.trim(),localStorage.setItem("agent-thread-id",h.threadId)});c("#regenThread").addEventListener("click",()=>{h.threadId=Be(),X.value=h.threadId,localStorage.setItem("agent-thread-id",h.threadId)});c("#clearChat").addEventListener("click",()=>{h.messages=[],h.activeTrace=[],h.streamingAnswer="",c("#traceList").innerHTML='<div class="empty-chat">会话已清空。</div>',c("#agentStatus").textContent="会话已清空。",G()});async function Ie(){const r=c("#query"),e=r.value.trim();if(!e){c("#agentStatus").textContent="请输入问题。";return}h.activeTrace=[],h.streamingAnswer="",V([]),$t(),Q("user",e),r.value="";try{const n=yt(c("#metadataFilters").value),s=await fetch(`${h.apiBase}/chat/agent`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e,thread_id:h.threadId,user_id:c("#userId").value.trim(),task_mode:null,metadata_filters:n})});if(!s.ok)throw new Error(await s.text());const t=document.createElement("pre"),l=await At(s,t),a=ze(l);V(a.trace),h.streamingAnswer="",c("#agentStatus").textContent="生成完成",Q("agent",a.answer||l||"空响应"),Y()}catch(n){Y(),h.streamingAnswer="",c("#agentStatus").textContent=`请求失败：${n.message}`,Q("agent",`请求失败：${n.message}`)}}c("#sendChat").addEventListener("click",Ie);c("#openRail").addEventListener("click",()=>ce(!h.railOpen));c("#closeRail").addEventListener("click",()=>ce(!1));c("#query").addEventListener("keydown",r=>{r.key==="Enter"&&!r.shiftKey&&(r.preventDefault(),Ie())});c("#uploadKnowledge").addEventListener("click",async()=>{const r=c("#knowledgeFile").files[0],e=c("#uploadResult");if(!r){e.textContent="请先选择文件。";return}try{const n=new FormData;n.append("file",r);const t=await(await fetch(`${h.apiBase}/knowledge/upload`,{method:"POST",body:n})).json();_(e,t)}catch(n){e.textContent=`上传失败：${n.message}`}});c("#rebuildEnv").addEventListener("click",async()=>{const r=c("#rebuildResult");T("showTestingPanel"),c("#evalStatus").textContent="正在重建测试环境...",r.textContent="正在重建测试环境...";try{const e=await q("/testing/rebuild",{method:"POST",body:JSON.stringify({force_download:c("#forceDownload").checked,run_retrieval_eval:c("#runRetrievalEvalAfterRebuild").checked})});_(r,e),e?.result?.retrieval_eval&&(h.latestRetrievalMetrics=e.result.retrieval_eval,I()),c("#evalStatus").textContent="测试环境重建完成。"}catch(e){r.textContent=`重建失败：${e.message}`,c("#evalStatus").textContent=`测试环境重建失败：${e.message}`}});c("#runRetrievalEval").addEventListener("click",async()=>{const r=c("#retrievalEvalResult");T("runRetrievalEval"),c("#evalStatus").textContent="正在运行 Retrieval Eval...",r.textContent="正在运行 retrieval eval...";try{const e=await q("/eval/retrieval",{method:"POST",body:JSON.stringify({top_k:Number(c("#topK").value),candidate_k:Number(c("#candidateK").value),strategy:c("#strategy").value})});_(r,e),h.latestRetrievalMetrics=e.metrics,I(),c("#evalStatus").textContent="Retrieval Eval 运行完成。"}catch(e){r.textContent=`retrieval eval 失败：${e.message}`,c("#evalStatus").textContent=`Retrieval Eval 失败：${e.message}`}});c("#runCompare").addEventListener("click",async()=>{const r=c("#compareResult");T("runCompare"),c("#evalStatus").textContent="正在运行 Baseline Compare...",r.textContent="正在运行 baseline compare...";try{const e=await q("/eval/retrieval/compare",{method:"POST",body:JSON.stringify({top_k:Number(c("#topK").value),candidate_k:Number(c("#candidateK").value),strategy:c("#strategy").value})});_(r,e),h.latestCompareReport=e.report;const n=e.report?.baselines?.find(s=>s.strategy===c("#strategy").value)||e.report?.baselines?.[e.report?.baselines?.length-1];n&&(h.latestRetrievalMetrics=n),I(),c("#evalStatus").textContent="Baseline Compare 运行完成。"}catch(e){r.textContent=`compare 失败：${e.message}`,c("#evalStatus").textContent=`Baseline Compare 失败：${e.message}`}});c("#runGenerationEval").addEventListener("click",async()=>{const r=c("#generationEvalResult");T("runGenerationEval"),c("#evalStatus").textContent="正在运行 Generation Eval...",r.textContent="正在运行 generation eval...";try{const e=await q("/eval/generation",{method:"POST",body:JSON.stringify({candidate_k:Number(c("#candidateK").value)})});_(r,e),c("#evalStatus").textContent="Generation Eval 运行完成。"}catch(e){r.textContent=`generation eval 失败：${e.message}`,c("#evalStatus").textContent=`Generation Eval 失败：${e.message}`}});c("#runBenchmark").addEventListener("click",async()=>{const r=c("#benchmarkResult");T("runBenchmark"),c("#evalStatus").textContent="正在运行 System Benchmark...",r.textContent="正在运行 system benchmark...";try{const e=await q("/eval/benchmark",{method:"POST",body:JSON.stringify({candidate_k:Number(c("#candidateK").value)})});_(r,e),h.latestBenchmarkMetrics=e.metrics,I(),c("#evalStatus").textContent="System Benchmark 运行完成。"}catch(e){r.textContent=`benchmark 失败：${e.message}`,c("#evalStatus").textContent=`System Benchmark 失败：${e.message}`}});c("#showTestingPanel").addEventListener("click",()=>{T("showTestingPanel"),c("#evalStatus").textContent="当前显示测试环境重建模块。"});G();I();ce(!1);T("runRetrievalEval");
