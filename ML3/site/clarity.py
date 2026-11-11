"""Plain-language layer for the OrthoTrace site: home-page explanation, a 'Start here' guide page, an 'In plain words'
note for every page, and a glossary that powers hover/focus definitions (assets/js/terms.js).

All numbers repeated here come from the saved study artifacts (see Results): pooled balanced accuracy 0.993-1.000 and
source-decoupled 0.498-0.686 for the five primary models; dimensions-only random forest 0.971 -> 0.333."""
import json
import re

# --------------------------------------------------------------------------------------------------------- glossary
# (key, display term, JS regex alternation, plain definition)
GLOSSARY = [
    ("balanced", "Balanced accuracy", r"balanced accuracy",
     "A fair score from 0 to 1: the average, over Hip, Knee and Shoulder, of how many images were named correctly. Random guessing scores about 0.33."),
    ("recall", "Recall", r"recall",
     "Of all the real hips, the share the model correctly called hip. Done per joint, then averaged."),
    ("pooled", "Pooled test", r"pooled",
     "All datasets are mixed and split at random, so test pictures look like the training pictures. An easy test."),
    ("decoupled", "Source-decoupled test", r"source-decoupled|decoupled|source-controlled",
     "A test on a dataset the model never saw during training. A hard and fair test of 'will it work somewhere new?'."),
    ("gap", "Generalization gap", r"generali[sz]ation gap",
     "The pooled score minus the new-dataset score. A big gap means the easy test was flattering the model."),
    ("source", "Dataset source", r"dataset sources?|data sources?",
     "The collection a picture came from, such as a hospital, a website or a research group."),
    ("checkpoint", "Checkpoint", r"checkpoints?",
     "A saved, trained model file. Our four checkpoints use the same network and differ only in the data they were trained on."),
    ("efficientnet", "EfficientNet-B3", r"EfficientNet-B3",
     "A well-known image-recognition neural network. All four checkpoints in the demo use it."),
    ("finetune", "Fine-tuning", r"fine-tun(?:ed|ing)",
     "Taking a network that already learned from millions of everyday photos and training it a little more on X-rays."),
    ("gradcam", "Grad-CAM", r"Grad-CAM",
     "A heat map showing which parts of the image pushed the model towards its answer. It shows sensitivity, not proof the model understands anatomy."),
    ("softmax", "Softmax confidence", r"softmax(?: score| confidence)?",
     "How the model splits 100% between its possible answers. It is not the chance of being right."),
    ("shortcutprobe", "Shortcut probe", r"shortcut probe",
     "A small model that sees only file properties (size, shape, format, file size), never the picture. If it gives the same answer, the answer could be a shortcut."),
    ("shortcut", "Shortcut", r"shortcuts?",
     "A clue that predicts the answer but has nothing to do with the real subject, like image size or file type."),
    ("rf", "Random forest", r"random forests?",
     "Many small decision trees that vote. Here it is given only image size and file properties, never the bones."),
    ("fracatlas", "FracAtlas", r"FracAtlas",
     "A public X-ray collection that contains all three joints. We use it as the 'new dataset' test."),
    ("provisional", "Provisional label", r"provisional(?: knee)? labels?",
     "A label from our team's visual check that a clinician has not yet reviewed."),
    ("calibration", "Calibration", r"calibration",
     "Whether '90% sure' really means right 90 times out of 100."),
    ("ece", "ECE", r"ECE",
     "Expected calibration error: how far the model's stated confidence is from how often it is actually right."),
    ("ood", "Out-of-distribution (OOD)", r"OOD|out-of-distribution",
     "An input unlike the training data, such as a hand X-ray shown to a hip, knee and shoulder model."),
    ("ci", "Confidence interval", r"confidence intervals?",
     "A range showing how much a score could wobble because the test set is finite. It is not a promise about future hospitals."),
    ("leakage", "Data leakage", r"leakage",
     "When test pictures secretly resemble training pictures, making scores look better than they are."),
    ("seed", "Seed", r"seeds?",
     "A number that fixes a run's randomness. Repeating with several seeds shows how stable a result is."),
]


TERMS_LOGIC = r"""
(function(){
 var T=(window.OT_TERMS||[]).map(function(t){return {k:t.k,d:t.d,re:new RegExp('\\b(?:'+t.re+')\\b','i')}});
 var main=document.getElementById('main'); if(!T.length||!main)return;
 var SKIP=/^(A|BUTTON|H1|H2|H3|H4|H5|H6|SCRIPT|STYLE|SVG|TEXTAREA|INPUT|SELECT|OPTION|ABBR|CODE|PRE|TH|SUMMARY|LABEL|CANVAS|FIGCAPTION|DT)$/i;
 var used={};
 function eligible(n){for(var p=n.parentNode;p&&p!==main;p=p.parentNode){
   if(SKIP.test(p.nodeName))return false;
   if(p.classList&&(p.classList.contains('no-terms')||p.classList.contains('term')||p.classList.contains('chart')||p.classList.contains('eyebrow')||p.classList.contains('menu')||p.classList.contains('request-stream')))return false}
   return true}
 function wrap(n){
   for(;;){
     var best=null;
     T.forEach(function(t){if(used[t.k])return;var m=t.re.exec(n.nodeValue);
       if(m&&(!best||m.index<best.m.index||(m.index===best.m.index&&m[0].length>best.m[0].length)))best={t:t,m:m}});
     if(!best)return;
     var m=best.m,txt=n.nodeValue,par=n.parentNode;
     var ab=document.createElement('abbr');ab.className='term';ab.tabIndex=0;ab.setAttribute('role','note');
     ab.setAttribute('data-tip',best.t.d);ab.setAttribute('aria-label',m[0]+': '+best.t.d);ab.textContent=m[0];
     var after=document.createTextNode(txt.slice(m.index+m[0].length));
     par.insertBefore(document.createTextNode(txt.slice(0,m.index)),n);par.insertBefore(ab,n);par.insertBefore(after,n);par.removeChild(n);
     used[best.t.k]=1;n=after}}
 function run(root){
   var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null),list=[];
   while(w.nextNode()){var n=w.currentNode;if(n.nodeValue.trim().length>3&&eligible(n))list.push(n)}
   list.forEach(wrap)}
 function place(e){var t=e.target.closest&&e.target.closest('.term');if(!t)return;
   var r=t.getBoundingClientRect();t.classList.toggle('term-r',r.left>innerWidth*0.55);t.classList.toggle('term-b',r.top<150)}
 document.addEventListener('mouseover',place);document.addEventListener('focusin',place);
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&document.activeElement&&document.activeElement.classList.contains('term'))document.activeElement.blur()});
 function start(){run(main);var out=document.getElementById('out');
   if(out&&window.MutationObserver){var busy=0;new MutationObserver(function(){if(busy)return;busy=1;setTimeout(function(){run(out);busy=0},250)}).observe(out,{childList:true})}}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
"""


def terms_js():
    data = [{"k": k, "re": rx, "d": d} for k, _t, rx, d in GLOSSARY]
    return ("/* Generated by clarity.py. Hover, tap or focus a dotted term for its plain-language meaning. */\nwindow.OT_TERMS="
            + json.dumps(data, ensure_ascii=False) + ";" + TERMS_LOGIC)


# ------------------------------------------------------------------------------------------------------------ home
HOME_PLAIN = '''<section id="start" class="cl-section" data-tone="light"><div class="wrap">
<span class="eyebrow">THE IDEA IN PLAIN WORDS</span>
<h2 class="cl-h2">A model can pass the test<br><em>without learning the subject.</em></h2>
<div class="cl-grid">
<div class="cl-story">
<p class="cl-big">Imagine a student who notices that every Maths paper in the practice pile is printed on blue paper.</p>
<p>In practice tests the student scores 100% by checking the paper colour. In the real exam the paper is white, and the student fails. The score measured the paper, not the subject.</p>
<p>X-ray AI can do the same. Public X-ray collections mostly hold <b>one joint each</b>, so picture size, borders and file type give the answer away. We tested whether the AI sees the <b>bone</b> or just the <b>dataset</b>.</p>
</div>
<figure class="cl-bars" aria-label="Balanced accuracy of five models: 0.99 to 1.00 on familiar pictures, 0.50 to 0.69 on a dataset never seen, 0.33 for random guessing">
<figcaption>Five models, two tests<small>1.00 = perfect · 0.33 = random guessing</small></figcaption>
<div class="cl-bar"><span>Familiar pictures</span><div class="cl-track"><i style="--w:99.5%"></i></div><b>0.99 – 1.00</b></div>
<div class="cl-bar warn"><span>A dataset it never saw</span><div class="cl-track"><i style="--w:60%"></i></div><b>0.50 – 0.69</b></div>
<div class="cl-bar chance"><span>Random guessing</span><div class="cl-track"><i style="--w:33.3%"></i></div><b>0.33</b></div>
<p>Balanced accuracy of the five main models, from the saved study results.</p>
</figure>
</div>
<div class="cl-trio">
<article><span>WHAT WE DID</span><h3>Two kinds of test</h3><p>We trained hip, knee and shoulder X-ray models on six public datasets, then tested them on familiar pictures and on a dataset they had never seen.</p></article>
<article><span>WHAT WE FOUND</span><h3>Scores fell by 31 to 50 points</h3><p>A model that only reads picture size got 97% on familiar data and 33% on new data, the same as guessing.</p></article>
<article><span>WHY IT MATTERS</span><h3>High scores can mislead</h3><p>A great score on a public dataset does not mean the AI works at a new hospital. Test on a new source before trusting a model.</p></article>
</div>
</div></section>
<section class="cl-section cl-tint" data-tone="light"><div class="wrap">
<span class="eyebrow">TRY IT IN THREE STEPS</span>
<h2 class="cl-h2">What to do on the demo page</h2>
<ol class="cl-steps">
<li><b>Pick an X-ray</b><p>Choose a sample image, or upload your own JPEG or PNG. Nothing is saved.</p></li>
<li><b>Read the answer</b><p>Four models name the joint and show how sure they are, with a heat map of what influenced them. If they disagree, the training data matters.</p></li>
<li><b>Check the shortcut probe</b><p>A blind model that sees only file size and format also guesses. If it agrees, the answer could be a shortcut.</p></li>
</ol>
<div class="cl-cta"><a class="btn primary" href="demo.html">Open the demo →</a><a class="btn" href="guide.html">Read the 2-minute guide ↗</a></div>
</div></section>
<section class="cl-section" data-tone="light"><div class="wrap">
<div class="cl-two">
<div><span class="eyebrow">WHAT THIS IS</span><h3>A tool for checking X-ray AI</h3>
<ul class="cl-list"><li>A study of whether hip, knee and shoulder X-ray AI learns anatomy or dataset clues.</li><li>A workbench that shows four models, a heat map and a shortcut check on one image.</li><li>Saved evidence you can inspect: scores, intervals and audits.</li></ul></div>
<div><span class="eyebrow">WHAT THIS IS NOT</span><h3>Not a medical device</h3>
<ul class="cl-list no"><li>It does not diagnose diseases or fractures.</li><li>It does not identify implant brands.</li><li>It has not been tested in hospitals.</li></ul></div>
</div>
</div></section>
'''


def tune_home(h):
    """Plain-language hero and section wording for the home page template."""
    def rep(old, new):
        nonlocal h
        assert old in h, "home template changed, cannot find: " + old[:60]
        h = h.replace(old, new, 1)
    rep("ORTHOPAEDIC AI · SOURCE-AWARE EVALUATION", "A STUDY OF X-RAY AI · HIP · KNEE · SHOULDER")
    rep("X-ray anatomy<br><em>Model comparison</em>", "Bone, or<br><em>dataset?</em>")
    rep("Score six anatomical regions in a radiograph. Compare four benchmark checkpoints on the same image to see how their training data affects the result.",
        "X-ray AI can score almost perfectly just by recognising which dataset a picture came from, not by understanding the bones. OrthoTrace shows when that happens, on any X-ray you choose.")
    rep('<a class="btn primary" href="demo.html">Open X-ray demo →</a><a class="btn hero-secondary" href="#model-comparison">Compare sample predictions ↗</a>',
        '<a class="btn primary" href="demo.html">Try the demo →</a><a class="btn hero-secondary" href="guide.html">New here? Start here ↗</a>')
    rep('<section id="problem"', HOME_PLAIN + '<section id="problem"')
    rep("DATASET SHORTCUTS", "A REAL EXAMPLE")
    rep("Models can learn dataset cues", "Same X-ray, different answers")
    rep("When a dataset mostly contains one joint, a model can use cues such as framing or image dimensions to guess the joint. Compare predictions from checkpoints trained with and without FracAtlas.",
        "This is one real X-ray from our test set. The first model was trained on all six datasets. The second was trained without the dataset this picture comes from. When the training data changes, the answer can change. That is what this project measures.")
    rep("THREE-CLASS BENCHMARK", "FOUR MODELS, ONE IMAGE")
    rep("pooled softmax score<br>for this sample’s predicted joint.", "how sure the first model is.<br>A score, not the chance of being right.")
    rep("DATASET SHORTCUT TEST", "THE SHORTCUT TEST")
    rep("Joint prediction from image size", "A model that never sees bones")
    rep("drop in balanced accuracy when source is decoupled. The random forest uses only width, height and aspect ratio.",
        "points lost when the test uses a dataset the model has never seen. This model looks only at a picture’s width, height and shape, not the bones, yet it scores 97% on familiar data.")
    rep("<h3>Pooled evaluation</h3><div><b>0.971</b><span>DIMENSIONS ONLY</span></div>", "<h3>Familiar data</h3><div><b>0.971</b><span>PICTURE SIZE ONLY</span></div>")
    rep("<h3>Source-controlled</h3><div><b>0.333</b><span>CHANCE LEVEL</span></div>", "<h3>New dataset</h3><div><b>0.333</b><span>SAME AS GUESSING</span></div>")
    return h


# ------------------------------------------------------------------------------------------------ plain-words notes
PLAIN = {
    "research.html": "The question we asked, the four predictions we wrote down before opening the test set, and what we did not try to prove.",
    "datasets.html": "Six public X-ray collections. Most hold one joint only, which is why an AI can cheat. Only FracAtlas holds all three joints.",
    "methodology.html": "How we kept the test fair: a plan locked in advance, a sealed test set opened once, and checks that the numbers can be reproduced.",
    "limitations.html": "What this study cannot tell you, such as whether the AI works in hospitals. Read this before you quote any number.",
    "paper.html": "The written paper and the files behind every number, ready to download.",
    "reproducibility.html": "How anyone can re-run the study, check the file fingerprints and see that the numbers match.",
    "about.html": "Who made this, what state it is in, and how to use it responsibly.",
    "context.html": "What an orthopaedic implant is, what its X-ray looks like, and what our AI is (and is not) asked to do.",
    "contribution.html": "What existed before, what we added, and how our tool differs from earlier work.",
    "literature.html": "What other researchers found about AI shortcuts in medical images, and the gap this project fills.",
    "timeline.html": "An interactive picture history of four implant designs. It explains why implant X-rays look the way they do.",
    "border-audit.html": "We repaint only the border of an X-ray and check whether the AI changes its mind. If it does, it is reading the border, not the bone.",
    "evaluation.html": "A map of the project: where each part is documented and what is still open.",
    "robustness.html": "Each bar is a model's score. One setting tests on familiar pictures, the other on a dataset the model never saw. The gap between them is what we measure.",
    "results.html": "The charts behind our claim. For every model, compare the score on familiar pictures with the score on a new dataset.",
}

DEMO_HOW = '''<section class="cl-how"><div class="wrap">
<ol class="cl-steps compact">
<li><b>Choose</b><p>Pick a sample on the left, or drop in your own X-ray.</p></li>
<li><b>Read</b><p>See the joint the models name, how sure they are, and whether the four models agree.</p></li>
<li><b>Check</b><p>Scroll the report to the heat map and the shortcut probe. They show what the answer might be based on.</p></li>
</ol>
</div></section>'''


def plain_note(text):
    return ('<section class="cl-plain"><div class="wrap"><aside class="plain-note"><b>In plain words</b>'
            f'<p>{text}</p><a href="guide.html">New here? Start with the 2-minute guide →</a></aside></div></section>')


def add_plain(fn, html):
    """Insert the 'In plain words' note (or the demo's how-to strip) right after the page head section."""
    block = DEMO_HOW if fn == "demo.html" else (plain_note(PLAIN[fn]) if fn in PLAIN else "")
    if not block:
        return html
    m = re.search(r'<section class="phead">.*?</section>', html, flags=re.S)
    if not m:
        return html
    return html[:m.end()] + block + html[m.end():]


# ----------------------------------------------------------------------------------------------------------- guide
TOUR = [
    ("index.html#start", "The idea", "Two minutes on why an X-ray AI can look perfect and still be unreliable."),
    ("demo.html?sample=2", "A normal result", "Sample 2. Four models agree. Open the heat map and the shortcut probe."),
    ("demo.html?sample=6", "A puzzle", "Sample 6 looks like an elbow, but was labelled knee. See how the models cope."),
    ("results.html#t-short", "The shortcut test", "A model that never sees bones, and still scores 97% on familiar data."),
    ("results.html#t-gap", "The gap", "Every main model, tested two ways. See how far the scores fall."),
    ("border-audit.html", "The border experiment", "Same X-ray, different borders. Does the AI change its mind?"),
    ("limitations.html", "What we did not prove", "Honest limits. Read this before quoting any number."),
]

PAGES = [
    ("demo.html", "Demo", "Upload or pick an X-ray. See four models, a heat map and a shortcut check.", "Open this first to see the idea working."),
    ("results.html", "Results", "Charts and tables for every model, tested two ways.", "Open this to check the numbers."),
    ("robustness.html", "Robustness", "Switch between easy and hard tests and watch each score change.", "Open this to feel the gap."),
    ("methodology.html", "Methodology", "How the study was run and how the test set was kept sealed.", "Open this to see why the test is fair."),
    ("datasets.html", "Datasets", "The six public collections and what each contains.", "Open this to see where the pictures come from."),
    ("literature.html", "Literature survey", "What other researchers found, and the gap we fill.", "Open this for the background."),
    ("border-audit.html", "Border audit", "Repaint only the border of an X-ray and see if the AI reacts.", "Open this for a second kind of shortcut test."),
    ("evaluation.html", "Evidence", "Where each part of the project is documented and what is open.", "Open this to find the proof."),
    ("limitations.html", "Limitations", "What the study cannot tell you.", "Read this before quoting a number."),
]

NUMBERS = [
    ("1.00", "A perfect score", "Every image named correctly."),
    ("0.33", "Random guessing", "With three joints to choose from, guessing gets one in three right."),
    ("0.99 – 1.00", "Familiar pictures", "Our five main models on the easy, mixed test."),
    ("0.50 – 0.69", "A dataset never seen", "The same models on the hard, fair test."),
    ("31 – 50 points", "The gap", "How much the easy test flattered the models."),
    ("0.971 → 0.333", "A model that never sees bones", "It reads only picture size. Easy test, then new dataset."),
]

FAQ = [
    ("Is this a medical tool?", "No. It is an academic research project. It does not diagnose anything, has not been tested in hospitals and must not be used for patient care."),
    ("What does the AI actually predict?", "Whether an X-ray shows a hip, a knee or a shoulder. A second model also flags hand, leg and elbow. It does not detect fractures, diseases or implant brands."),
    ("Why are there four models for one image?", "They are the same type of network, trained on different data. One saw everything. The others each missed one dataset. If they disagree on an image, the training data is changing the answer."),
    ("What is the shortcut probe?", "A small model that sees only file properties: width, height, shape, format and file size. It never sees the picture. If it names the same joint as the main model, that answer could come from a shortcut instead of anatomy."),
    ("Does a matching probe prove the model cheated?", "No. It only shows the answer could be produced without looking at bones. A disagreement does not prove the model understands anatomy either."),
    ("Why do scores fall on a new dataset?", "Because each dataset has its own habits: picture size, borders, file type. A model can learn those habits instead of the anatomy. On a new dataset the habits change and the score collapses."),
    ("Can I trust a high score on a public dataset?", "Only if the model was also tested on a dataset it never saw. That is the main lesson of this project."),
    ("Why does the online demo not run live?", "The public site is static hosting, so it can only show saved samples. Live upload, the heat map and the shortcut probe need the Python server, which you can start on your own computer with start.ps1."),
    ("Is my image stored?", "No. On the live server an uploaded image is processed in memory and discarded. Do not upload images that could identify a patient."),
    ("What is still unproven?", "Clinical use, the cause of the failures (implants are a suspect, not proven), and performance at a new hospital. The limitations page lists everything."),
]


def guide_page(page, head, sec):
    tour = "".join(f'<li><a href="{h}"><span>{i:02d}</span><b>{t}</b><em>{d}</em></a></li>' for i, (h, t, d) in enumerate(TOUR, 1))
    cards = "".join(f'<a class="gd-card" href="{h}"><h3>{t}</h3><p>{d}</p><small>{w} →</small></a>' for h, t, d, w in PAGES)
    nums = "".join(f'<div><b>{n}</b><h3>{t}</h3><p>{d}</p></div>' for n, t, d in NUMBERS)
    gloss = "".join(f'<div><dt>{t}</dt><dd>{d}</dd></div>' for _k, t, _rx, d in GLOSSARY)
    faq = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)
    body = head("Start here", "Understand this website<br><em>in two minutes.</em>",
                "OrthoTrace asks one question: when an AI names the joint in an X-ray, is it looking at the bone, or just at the dataset the picture came from? This page explains what you will see and how to read it.")
    body += sec('''<div class="cl-grid">
<div class="cl-story"><p class="cl-big">A high score is not proof of understanding.</p>
<p>Public X-ray collections mostly hold one joint each. A model can learn "this size of picture means hip" and score almost perfectly, then fail on pictures from somewhere new. We measured how often that happens and built a tool that lets you see it on any X-ray.</p>
<p>The short version: on familiar pictures our five main models score <b>0.99 to 1.00</b>. On a dataset they never saw, they score <b>0.50 to 0.69</b>. Random guessing scores 0.33.</p>
<div class="cl-cta"><a class="btn primary" href="demo.html">Try the demo →</a><a class="btn" href="index.html#start">See the idea on the home page ↗</a></div></div>
<figure class="cl-bars"><figcaption>Five models, two tests<small>1.00 = perfect · 0.33 = random guessing</small></figcaption>
<div class="cl-bar"><span>Familiar pictures</span><div class="cl-track"><i style="--w:99.5%"></i></div><b>0.99 – 1.00</b></div>
<div class="cl-bar warn"><span>A dataset it never saw</span><div class="cl-track"><i style="--w:60%"></i></div><b>0.50 – 0.69</b></div>
<div class="cl-bar chance"><span>Random guessing</span><div class="cl-track"><i style="--w:33.3%"></i></div><b>0.33</b></div></figure></div>''', "cl-section", "idea")
    body += sec(f'<span class="eyebrow">A FIVE-MINUTE TOUR</span><h2 class="cl-h2">Follow these seven stops</h2><ol class="gd-tour">{tour}</ol>', "cl-section cl-tint", "tour")
    body += sec(f'<span class="eyebrow">WHAT IS ON EACH PAGE</span><h2 class="cl-h2">Where to find what</h2><div class="gd-cards">{cards}</div>', "cl-section", "pages")
    body += sec(f'<span class="eyebrow">HOW TO READ THE NUMBERS</span><h2 class="cl-h2">Six numbers that tell the story</h2><div class="gd-numbers">{nums}</div><p class="cl-foot">All values come from the saved study results. Balanced accuracy is explained in the glossary below.</p>', "cl-section cl-tint", "numbers")
    body += sec(f'<span class="eyebrow">PLAIN-WORDS GLOSSARY</span><h2 class="cl-h2">Words you will meet</h2><p class="cl-foot">On every page, dotted words show their meaning when you hover over them or tap them.</p><dl class="gd-gloss no-terms">{gloss}</dl>', "cl-section", "glossary")
    body += sec(f'<span class="eyebrow">QUESTIONS PEOPLE ASK</span><h2 class="cl-h2">Short answers</h2><div class="gd-faq">{faq}</div>', "cl-section cl-tint", "faq")
    body += sec('<div class="callout warn"><b>Project scope</b>The models classify Hip, Knee or Shoulder. This project evaluates <i>how joint-recognition models are tested</i>. It is an academic project, not a medical device, and it does not diagnose disease or identify implant brands.</div>', "tight")
    return page("guide.html", "Start here", "A two-minute plain-language guide to what OrthoTrace shows and how to read it.", body)
