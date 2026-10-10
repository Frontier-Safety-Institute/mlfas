from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
# Preserve selectable SVG text; drawings remain genuine vector paths, not a raster wrapped in SVG.
matplotlib.rcParams['svg.fonttype'] = 'none'
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
import nbformat as nbf
import json, re, textwrap, zipfile, hashlib, math

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT/'images'
IMG.mkdir(parents=True, exist_ok=True)
NAVY='#162944'; TEAL='#007f84'; GOLD='#c17b16'; LIGHT='#f0f6fa'; MUTED='#52677d'; RED='#b53f44'; GREEN='#2a8157'; WHITE='#ffffff'


def figsave(fig,name):
    # Export both representations from ONE matplotlib source figure so dimensions,
    # labels and colors are identical. The SVG is the canonical illustration;
    # the PNG is a browser/renderer fallback (and quick preview).
    stem = Path(name).stem
    fig.savefig(IMG/f'{stem}.svg',format='svg',bbox_inches='tight',pad_inches=.23,facecolor='white')
    fig.savefig(IMG/f'{stem}.png',format='png',dpi=170,bbox_inches='tight',pad_inches=.23,facecolor='white')
    plt.close(fig)


def init_fig(w=10,h=4.1, title=None):
    fig, ax=plt.subplots(figsize=(w,h))
    ax.set_xlim(0,w);ax.set_ylim(0,h);ax.axis('off')
    if title: ax.text(.2,h-.25,title,color=NAVY,fontsize=17,weight='bold',ha='left',va='top')
    return fig,ax


def grid(ax,x,y,data,headers=None,rowlabels=None,cellw=1.15,cellh=.55,headcolor=NAVY,highlights=None,fontsize=11,labelwidth=1.08):
    """True rectangular grid with one value per cell and explicit borders."""
    data=[[str(v) for v in row] for row in data]
    nr=len(data);nc=len(data[0]); hh=cellh if headers else 0
    if rowlabels:
        ax.add_patch(Rectangle((x,y),labelwidth,cellh*nr+hh,facecolor='white',edgecolor='none'))
    for j in range(nc):
        if headers:
            xx=x+(labelwidth if rowlabels else 0)+j*cellw
            ax.add_patch(Rectangle((xx,y+nr*cellh),cellw,cellh,facecolor=headcolor,edgecolor='white',linewidth=1))
            ax.text(xx+cellw/2,y+(nr+.5)*cellh,str(headers[j]),color='white',ha='center',va='center',fontsize=fontsize-.5,weight='bold')
    if rowlabels:
        ax.add_patch(Rectangle((x,y+nr*cellh),labelwidth,cellh,facecolor=headcolor,edgecolor='white',linewidth=1))
        ax.text(x+labelwidth/2,y+(nr+.5)*cellh,('Outcome' if str(rowlabels[0]).startswith('Pass') else 'Index' if str(rowlabels[0]).startswith('row ') else 'Learner'),color='white',ha='center',va='center',fontsize=fontsize-.5,weight='bold')
    for i in range(nr):
        yy=y+(nr-1-i)*cellh
        if rowlabels:
            ax.add_patch(Rectangle((x,yy),labelwidth,cellh,facecolor=LIGHT,edgecolor='#91a4b8',linewidth=1))
            ax.text(x+labelwidth/2,yy+cellh/2,str(rowlabels[i]),color=NAVY,ha='center',va='center',fontsize=fontsize)
        for j in range(nc):
            xx=x+(labelwidth if rowlabels else 0)+j*cellw
            bgcolor='#fff0cf' if highlights and (i,j) in highlights else ('#f3f7fa' if i%2 else '#fff')
            ax.add_patch(Rectangle((xx,yy),cellw,cellh,facecolor=bgcolor,edgecolor='#879aaf',linewidth=1.25))
            ax.text(xx+cellw/2,yy+cellh/2,data[i][j],color=NAVY,fontsize=fontsize,va='center',ha='center',weight='bold' if highlights and (i,j) in highlights else 'normal')
    return (labelwidth if rowlabels else 0)+nc*cellw, nr*cellh+hh


def block(ax,x,y,w,h,title,detail, color=TEAL):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.07,rounding_size=0.13',facecolor='#f5f9fb',edgecolor=color,linewidth=2))
    ax.text(x+w/2,y+h*.65,title,color=NAVY,weight='bold',fontsize=13,ha='center',va='center')
    ax.text(x+w/2,y+h*.26,detail,color=MUTED,fontsize=10,ha='center',va='center')

def arrow(ax,x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=18,lw=2,color=TEAL))

# 01 proper table
fig,ax=init_fig(10,4.3,'A dataset is a table: every cell belongs to one row and one column')
grid(ax,1.2,.8,[[1,2,3],[2,4,5],[3,6,7],[4,8,9]],['Hours','Practice','Score'],['Alice','Ben','Chika','Dara'],cellw=1.55,cellh=.57,fontsize=12,highlights={(1,2)})
ax.text(7.1,2.8,'4 rows = 4 learners',fontsize=13,color=NAVY,weight='bold')
ax.text(7.1,2.25,'3 columns = 3 values each',fontsize=12,color=MUTED)
ax.text(7.1,1.64,'Highlighted cell:',fontsize=12,color=MUTED)
ax.text(7.1,1.26,'Ben · Score = 5',fontsize=13,color=GOLD,weight='bold')
ax.text(1.2,.33,'The names label rows but are not part of the numeric tensor.',fontsize=10,color=MUTED)
figsave(fig,'01-table-rows-columns.png')

# 02 shapes
fig,ax=init_fig(11,3.65,'One idea, different shapes')
ax.text(1.0,2.68,'Scalar',color=NAVY,fontsize=14,weight='bold',ha='center')
grid(ax,.53,1.9,[[3]],cellw=.95,cellh=.62)
ax.text(1.0,1.54,'shape ( )',color=MUTED,fontsize=11,ha='center')
ax.text(4.0,2.68,'Vector',color=NAVY,fontsize=14,weight='bold',ha='center')
grid(ax,2.2,1.91,[[1,2,3,4]],cellw=.9,cellh=.62)
ax.text(4.0,1.54,'shape (4,)',color=MUTED,fontsize=11,ha='center')
ax.text(8.65,2.68,'Matrix',color=NAVY,fontsize=14,weight='bold',ha='center')
grid(ax,7.1,1.36,[[1,2,3],[4,5,6]],cellw=1.04,cellh=.56)
ax.text(8.65,.88,'shape (2, 3) = 2 rows × 3 columns',color=MUTED,fontsize=10,ha='center')
figsave(fig,'02-tensor-shapes.png')

# 03 index
fig,ax=init_fig(10,4.2,'Tensor indexing: positions start at 0')
grid(ax,.65,.8,[[1,2,3],[2,4,5],[3,6,7],[4,8,9]],['col 0','col 1','col 2'],['row 0','row 1','row 2','row 3'],cellw=1.26,cellh=.57,labelwidth=1.2,highlights={(1,2)})
ax.text(6.2,2.73,'tensor[1, 2]  →  5',color=GOLD,fontsize=16,weight='bold')
ax.text(6.2,2.2,'row index 1 = second row',color=MUTED,fontsize=12)
ax.text(6.2,1.82,'column index 2 = third column',color=MUTED,fontsize=12)
ax.text(6.2,1.2,'tensor[:, 0]  →  [1, 2, 3, 4]',color=NAVY,fontsize=12)
figsave(fig,'03-indexing.png')

# 04 broadcasting
fig,ax=init_fig(12.6,4.25,'Broadcasting: shape (3, 1) + shape (1, 2) → shape (3, 2)')
ax.text(1.55,3.36,'A: 3 rows, 1 column',ha='center',fontsize=11,color=NAVY,weight='bold')
grid(ax,1.1,1.06,[[1],[2],[3]],cellw=.9,cellh=.60)
ax.text(3.35,2.05,'+',fontsize=26,ha='center',color=TEAL,weight='bold')
ax.text(5.7,3.36,'B: 1 row, 2 columns',ha='center',fontsize=11,color=NAVY,weight='bold')
grid(ax,4.69,1.67,[[10,20]],cellw=1.02,cellh=.60)
ax.text(7.54,2.05,'=',fontsize=26,ha='center',color=TEAL,weight='bold')
ax.text(10.2,3.36,'Result: 3 rows, 2 columns',ha='center',fontsize=11,color=NAVY,weight='bold')
grid(ax,9.16,1.06,[[11,21],[12,22],[13,23]],cellw=1.06,cellh=.60)
ax.text(6.25,.51,'Each cell is A[row, 0] + B[0, column].',ha='center',fontsize=11,color=MUTED)
figsave(fig,'04-broadcasting.png')

# 05 pipeline
fig,ax=init_fig(11.5,3.3,'From raw observations to model-ready numbers')
block(ax,.33,.95,3.15,1.43,'Raw table','missing values + words',RED)
arrow(ax,3.64,1.65,4.1,1.65)
block(ax,4.27,.95,3.0,1.43,'Clean features','fill missing · encode text',TEAL)
arrow(ax,7.44,1.65,7.88,1.65)
block(ax,8.05,.95,3.15,1.43,'Numeric tensor','rows × columns',GREEN)
figsave(fig,'05-cleaning-pipeline.png')

# 06 missing
fig,ax=init_fig(12.5,5.4,'Missing information: identify it, then choose a treatment')
ax.text(3.15,4.45,'Before: missing cell',ha='center',color=NAVY,weight='bold',fontsize=13)
grid(ax,.52,1.25,[[1,'2'],[2,'?'],[3,6],[4,8]],['Hours','Practice'],['Alice','Ben','Chika','Dara'],cellw=1.5,cellh=.57,highlights={(1,1)})
arrow(ax,6.05,2.6,6.57,2.6)
ax.text(9.55,4.45,'After: filled using observed mean',ha='center',color=NAVY,weight='bold',fontsize=13)
grid(ax,7.05,1.25,[[1,'2.00'],[2,'5.33'],[3,'6.00'],[4,'8.00']],['Hours','Practice'],['Alice','Ben','Chika','Dara'],cellw=1.56,cellh=.57,highlights={(1,1)})
ax.text(6.25,.55,'Observed Practice mean: (2 + 6 + 8) / 3 = 5.33',ha='center',color=MUTED,fontsize=11)
figsave(fig,'06-missing-values.png')

# 07 features and target: accurate semantics: targets NEVER come from model as direct output
fig,ax=init_fig(12.9,5.35,'Features, predictions, and targets have distinct roles')
ax.text(1.95,4.43,'Input features  X',ha='center',fontsize=13,color=TEAL,weight='bold')
grid(ax,.42,1.46,[[1,2],[2,'5.33'],[3,6],[4,8]],['Hours','Practice'],['Alice','Ben','Chika','Dara'],cellw=1.29,cellh=.54,fontsize=11)
arrow(ax,4.20,2.65,4.56,2.65)
block(ax,4.70,2.06,1.67,1.17,'Model','combines X')
arrow(ax,6.51,2.65,6.89,2.65)
ax.text(7.62,4.43,'Predicted  ŷ',ha='center',fontsize=13,color=TEAL,weight='bold')
grid(ax,7.03,1.47,[[4],[5],[6],[8]],['Estimate'],cellw=1.19,cellh=.54)
ax.text(8.97,2.64,'vs.',ha='center',fontsize=16,color=MUTED,weight='bold')
ax.text(10.63,4.43,'Observed  y',ha='center',fontsize=13,color=GOLD,weight='bold')
grid(ax,10.00,1.47,[[3],[5],[7],[9]],['Score'],cellw=1.24,cellh=.54)
ax.text(6.45,.66,'Compare predictions with known targets to calculate error. The target is not a model input.',ha='center',fontsize=11.4,color=MUTED)
figsave(fig,'07-feature-target.png')

# 08 one hot
fig,ax=init_fig(12,4.35,'One-hot encoding: labels become numeric columns')
ax.text(2.0,3.38,'Text feature',ha='center',color=NAVY,weight='bold',fontsize=13)
grid(ax,1.4,1.0,[['Video'],['Text'],['Video'],['Text']],['Method'],cellw=1.2,cellh=.42,fontsize=11)
arrow(ax,4.22,1.98,4.92,1.98)
ax.text(8.5,3.38,'Two numeric feature columns',ha='center',color=NAVY,weight='bold',fontsize=13)
grid(ax,6.42,1.0,[[1,0],[0,1],[1,0],[0,1]],['is_Video','is_Text'],cellw=2.02,cellh=.42,fontsize=11)
ax.text(6.5,.46,'No invented numerical ordering between “Video” and “Text”.',ha='center',color=MUTED,fontsize=11)
figsave(fig,'08-one-hot-encoding.png')

# 09 dot
fig,ax=init_fig(11.2,3.55,'Dot product: multiply matching positions, then add')
ax.text(2.25,2.85,'Example inputs x',ha='center',fontsize=13,color=NAVY,weight='bold')
grid(ax,.95,1.8,[[2,4]],cellw=1.3,cellh=.66)
ax.text(4.2,2.12,'·',fontsize=29,color=TEAL,ha='center')
ax.text(6.3,2.85,'Weights w',ha='center',fontsize=13,color=NAVY,weight='bold')
grid(ax,5.1,1.8,[[3,1]],cellw=1.3,cellh=.66)
ax.text(7.92,2.12,'=',fontsize=25,color=TEAL,ha='center')
ax.text(9.72,2.15,'10',ha='center',fontsize=30,color=GREEN,weight='bold')
ax.text(5.6,1.02,'(2 × 3) + (4 × 1) = 6 + 4 = 10',ha='center',fontsize=14,color=NAVY)
figsave(fig,'09-dot-product.png')

# 10 matvec
fig,ax=init_fig(12.2,4.85,'Matrix–vector multiplication: one prediction per row')
ax.text(2.0,4.06,'X  (4 × 2)',fontsize=13,color=NAVY,weight='bold',ha='center')
grid(ax,.53,1.25,[[1,1],[2,1],[3,1],[4,1]],['Hours','Bias 1'],cellw=1.48,cellh=.53)
ax.text(4.25,2.55,'@',fontsize=24,color=TEAL,ha='center')
ax.text(5.73,4.06,'w  (2 × 1)',fontsize=13,color=NAVY,weight='bold',ha='center')
grid(ax,5.20,2.13,[[2],[1]],cellw=1.07,cellh=.60)
ax.text(7.25,2.55,'=',fontsize=23,color=TEAL,ha='center')
ax.text(9.0,4.06,'Predictions  (4 × 1)',fontsize=13,color=NAVY,weight='bold',ha='center')
grid(ax,8.45,1.25,[[3],[5],[7],[9]],cellw=1.1,cellh=.53)
ax.text(5.7,.66,'First row: 1 × 2 + 1 × 1 = 3    •    Last row: 4 × 2 + 1 × 1 = 9',ha='center',fontsize=12,color=MUTED)
figsave(fig,'10-matrix-vector.png')

# 11 matmat
fig,ax=init_fig(13,4.15,'Matrix multiplication: matching inner dimensions')
ax.text(2.3,3.40,'A : 2 × 3',color=NAVY,fontsize=13,ha='center',weight='bold')
grid(ax,.88,1.69,[[1,2,3],[4,5,6]],cellw=.94,cellh=.57)
ax.text(4.65,2.27,'@',fontsize=24,color=TEAL,ha='center')
ax.text(6.45,3.40,'B : 3 × 2',color=NAVY,fontsize=13,ha='center',weight='bold')
grid(ax,5.52,1.38,[[1,0],[0,1],[1,1]],cellw=.94,cellh=.57)
ax.text(8.24,2.27,'=',fontsize=23,color=TEAL,ha='center')
ax.text(10.22,3.40,'C : 2 × 2',color=NAVY,fontsize=13,ha='center',weight='bold')
grid(ax,9.25,1.69,[[4,5],[10,11]],cellw=.94,cellh=.57,highlights={(0,0)})
ax.text(6.5,.68,'C[0, 0] = 1×1 + 2×0 + 3×1 = 4     •     Each output is a row–column dot product.',ha='center',fontsize=11,color=MUTED)
figsave(fig,'11-matrix-matrix.png')

# 12 norms
fig,ax=plt.subplots(figsize=(8.2,4.4))
ax.plot([0,3],[0,0],lw=3,color=TEAL); ax.plot([3,3],[0,4],lw=3,color=GOLD); ax.plot([0,3],[0,4],lw=3,color=NAVY)
ax.set_xlim(-1,5.7);ax.set_ylim(-.6,5.5);ax.set_aspect('equal');ax.axis('off')
ax.text(1.3,-.4,'3',color=TEAL,fontsize=16,weight='bold');ax.text(3.25,2,'4',color=GOLD,fontsize=16,weight='bold')
ax.text(1.35,2.55,'length = 5',color=NAVY,fontsize=16,weight='bold',rotation=54)
ax.text(-.85,5.05,'L2 norm measures the length of a vector',color=NAVY,fontsize=16,weight='bold')
ax.text(3.9,3.4,'v = [3, 4]',color=NAVY,fontsize=13)
ax.text(3.9,2.75,'‖v‖₂ = √(3²+4²)',color=MUTED,fontsize=13)
ax.text(3.9,2.18,'= √25 = 5',color=GREEN,fontsize=14,weight='bold')
figsave(fig,'12-vector-norm.png')

# 13 tangent
x=np.linspace(-.2,4.0,200); fig,ax=plt.subplots(figsize=(9.5,4.5))
ax.plot(x,x*x,color=NAVY,lw=2.8,label='f(x) = x²'); ax.plot(x,4+4*(x-2),color=GOLD,lw=2.3,ls='--',label='tangent at x = 2')
ax.scatter([2],[4],s=85,zorder=5,color=TEAL)
ax.annotate('x = 2, f(x) = 4\nslope f\u2032(2) = 4',xy=(2,4),xytext=(2.6,5.6),fontsize=11,color=NAVY,arrowprops={'arrowstyle':'->','color':TEAL})
ax.set_xlim(0,4);ax.set_ylim(0,13);ax.set_xlabel('x (input)');ax.set_ylabel('f(x) (output)');ax.legend(loc='upper left',frameon=False)
ax.set_title('A derivative is the local slope of a curve',loc='left',color=NAVY,fontsize=15,weight='bold');ax.grid(alpha=.14)
figsave(fig,'13-derivative-tangent.png')

# 14 forward graph
fig,ax=init_fig(12.7,3.85,'Forward pass: compute a prediction and its error')
block(ax,.35,1.46,2.0,1.26,'Input x = 2','weight w = 1')
arrow(ax,2.5,2.08,3.12,2.08)
block(ax,3.27,1.46,2.15,1.26,'Prediction = 3','w × x + b = 3')
arrow(ax,5.58,2.08,6.17,2.08)
block(ax,6.33,1.46,2.35,1.26,'Difference = −2','prediction − target 5')
arrow(ax,8.84,2.08,9.36,2.08)
block(ax,9.52,1.46,2.67,1.26,'Squared error = 4','(−2)² = 4',GOLD)
ax.text(6.2,.66,'Forward = calculate values; no gradients or weight update yet.',ha='center',color=MUTED,fontsize=12)
figsave(fig,'14-forward-graph.png')

# 15 backward graph
fig,ax=init_fig(12.8,4.35,'Backward pass: follow the chain rule from loss to weight')
block(ax,.29,1.7,2.54,1.24,'L = (ŷ − 5)²','dL / dŷ = −4',GOLD)
arrow(ax,3.0,2.31,3.62,2.31)
block(ax,3.77,1.7,2.48,1.24,'ŷ = 2w + 1','dŷ / dw = 2',TEAL)
arrow(ax,6.45,2.31,7.06,2.31)
block(ax,7.21,1.7,4.7,1.24,'dL / dw = (−4) × 2 = −8','a negative gradient means increase w',GREEN)
ax.text(6.25,1.05,'Weight update: w_new = 1 − 0.1 × (−8) = 1.8',color=NAVY,ha='center',fontsize=13,weight='bold')
ax.text(6.25,.52,'New prediction = 2×1.8 + 1 = 4.6    •    new squared error = 0.16',color=MUTED,ha='center',fontsize=11)
figsave(fig,'15-backward-chain-rule.png')

# 16 curve
fig,ax=plt.subplots(figsize=(9.5,4.7))
w=np.linspace(.3,3.5,300); L=(2*w-4)**2
ax.plot(w,L,color=NAVY,lw=2.6)
ax.scatter([1,1.8,2],[4,.16,0],color=[RED,GREEN,TEAL],s=[95,95,70],zorder=4)
ax.annotate('Start w=1\nloss=4',xy=(1,4),xytext=(.50,5.6),fontsize=11,color=RED,arrowprops={'arrowstyle':'->','color':RED})
ax.annotate('Updated w=1.8\nloss=0.16',xy=(1.8,.16),xytext=(2.22,2.7),fontsize=11,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
ax.annotate('Minimum w=2',xy=(2,0),xytext=(2.6,.70),fontsize=11,color=TEAL,arrowprops={'arrowstyle':'->','color':TEAL})
ax.set_xlim(.3,3.5);ax.set_ylim(-.3,12);ax.set_xlabel('Weight w');ax.set_ylabel('Squared error L(w)');ax.grid(alpha=.16)
ax.set_title('One gradient step can reduce the error',loc='left',color=NAVY,fontsize=15,weight='bold')
figsave(fig,'16-gradient-step.png')

# 17 coin two tosses
fig,ax=init_fig(11.2,4.2,'Two independent fair coin tosses have four equally likely outcomes')
block(ax,.35,1.65,1.5,1.05,'Start','')
for title,yy in [('H',2.55),('T',1.05)]:
    ax.text(4.0,yy,title,fontsize=14,ha='center',weight='bold',color=NAVY)
arrow(ax,1.96,2.20,3.48,2.62);arrow(ax,1.96,2.12,3.48,1.37)
for ypos,txt in [(3.18,'HH'),(2.27,'HT'),(1.4,'TH'),(.49,'TT')]:
    ax.add_patch(FancyBboxPatch((8.07,ypos-.29),1.62,.57,boxstyle='round,pad=.04',edgecolor='#9eaec2',facecolor=LIGHT))
    ax.text(8.88,ypos,txt+'  ¼',ha='center',va='center',fontsize=14,color=NAVY,weight='bold')
for xx,yy,ends in [(4.3,2.65,[3.18,2.27]),(4.3,1.25,[1.4,.49])]:
    for k,fin in enumerate(ends): arrow(ax,xx,yy,8.02,fin)
ax.text(5.88,.23,'P(exactly one head) = P(HT or TH) = ¼ + ¼ = ½',fontsize=11,color=MUTED,ha='center')
figsave(fig,'17-coin-outcomes.png')

# 18 frequency plot
rng=np.random.default_rng(7)
coin=rng.integers(0,2,1000); running=np.cumsum(coin)/np.arange(1,1001)
fig,ax=plt.subplots(figsize=(9.7,4.6));ax.plot(range(1,1001),running,color=TEAL,lw=1.7,label='Observed fraction of heads')
ax.axhline(.5,ls='--',color=GOLD,lw=2,label='Theoretical probability: 0.5')
ax.set_xlim(1,1000);ax.set_ylim(.2,.8);ax.set_xlabel('Number of tosses');ax.set_ylabel('Observed proportion of heads')
ax.set_title('With more tosses, observed frequency tends to stabilize',loc='left',color=NAVY,fontsize=14,weight='bold')
ax.legend(loc='upper right',frameon=False,fontsize=10);ax.grid(alpha=.13)
figsave(fig,'18-sample-size.png')

# 19 contingency
fig,ax=init_fig(11.5,4.25,'A small 2 × 2 count table: conditional probability')
# values under groups Hours>=3 pass yes/no; two groups and totals
labels=['Pass (≥ 6)','Not pass (< 6)','Total']
grid(ax,1.10,.92,[[2,0,2],[0,2,2],[2,2,4]],['Hours ≥ 3','Hours < 3','Total'],labels,cellw=1.48,cellh=.57,labelwidth=1.6,fontsize=10.5,highlights={(0,0)})
ax.text(7.48,2.65,'P(pass | hours ≥ 3)',color=NAVY,fontsize=13,weight='bold')
ax.text(7.48,2.1,'= 2 / 2 = 1.0',color=GREEN,fontsize=16,weight='bold')
ax.text(7.48,1.38,'Only 4 made-up learners.',color=MUTED,fontsize=11)
ax.text(7.48,1.06,'Not a reliable real-world estimate.',color=MUTED,fontsize=10.5)
figsave(fig,'19-conditional-probability.png')

print('CREATED',len(list(IMG.glob('*.svg'))),'SVG illustrations and',len(list(IMG.glob('*.png'))),'PNG fallbacks')

# --- Notebook authoring -----------------------------------------------------
def M(source, tags=None):
    cell=nbf.v4.new_markdown_cell(textwrap.dedent(source).strip()+"\n")
    if tags: cell.metadata['tags']=tags
    return cell

def C(source, tags=None):
    cell=nbf.v4.new_code_cell(textwrap.dedent(source).strip()+"\n")
    if tags: cell.metadata['tags']=tags
    return cell

def pic(file,caption):
    # Standard <picture>: the browser prefers vector SVG; PNG is the fallback for
    # clients that do not support that media type. Works in Jupyter HTML export.
    # Use quote-safe alt/title strings without HTML injection.
    import html
    stem=Path(file).stem
    esc=html.escape(caption,quote=True)
    return M(f'<picture>\n  <source type="image/svg+xml" srcset="images/{stem}.svg">\n  <img src="images/{stem}.png" alt="{esc}" loading="lazy">\n</picture>\n\n*Figure: {caption}.*')

def base():
    return {"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
            "language_info":{"name":"python","version":"3.11"},
            "fsilearning":{"course":"FSI-MLFAS","chapter":2,"type":"interleaved-notebook","original_artwork":True}}

def mkbook(num, filename, name, cells):
    nb=nbf.v4.new_notebook(cells=cells,metadata=base());nb.metadata['fsilearning']['lesson']=num
    nbf.validate(nb)
    nbf.write(nb,ROOT/filename)
    print('Notebook',filename,'cells:',len(cells),'words:',sum(len(''.join(c.source).split()) for c in cells if c.cell_type=='markdown'))
    return nb

lesson1=[
M(r'''# 2.1 · Data manipulation and tensors

**Machine Learning Foundations for AI Safety · Chapter 2**  
**Estimated time:** 30–40 minutes · **Prerequisite:** knowing what a Python list is.

### What you will be able to do

- Explain a tensor using everyday examples, identify its **shape** and **axes**, and tell a scalar, vector and matrix apart.
- Select a cell or a row/column using Python indexing.
- Explain the difference between *elementwise arithmetic* and *broadcasting*.
- Run small PyTorch examples and predict their outputs before running them.

> **Our running example:** A made-up class of four learners. Each learner has study hours, completed practice questions, and a quiz score. We use synthetic numbers for easy arithmetic; they are not evidence that hours alone determine a real student's score.

**Learning method:** Read the idea → inspect the picture → predict the output → run the code → explain it in your own words.'''),
M(r'''## 1. What does “data” look like to a computer?

We may write **“Ben studied 2 hours, completed 4 questions, and scored 5.”** A computer can process this observation as three numbers: `[2, 4, 5]`. Put four learners together and we get a rectangular **table**.

A **row** describes *one learner*. A **column** describes *one type of measurement*. A **cell** is where a particular row meets a particular column; every cell stores exactly one value.

Here is the entire table. Count the four learner rows and three numeric columns. The table therefore has shape **(4, 3)**. The names help humans read the data, but the names are not included in this particular numeric matrix.'''),
pic('01-table-rows-columns.png','A fully labeled 4-row × 3-column data table with the cell for Ben’s quiz score highlighted'),
M(r'''For example, **row Ben + column Score = 5**. The table is not just a picture of cells: it is an organized way to tell the computer which value belongs where.

### Try this in Python

First build the numeric table with PyTorch, a library used widely in deep learning. We will not need a GPU or any downloaded dataset.'''),
C(r'''import torch

learner_names = ["Alice", "Ben", "Chika", "Dara"]
data = torch.tensor([
    [1., 2., 3.],  # Alice: hours, practice, score
    [2., 4., 5.],  # Ben
    [3., 6., 7.],  # Chika
    [4., 8., 9.],  # Dara
])

print('Shape:', tuple(data.shape))
print('Number of values:', data.numel())
print('First row:', data[0].tolist())
assert tuple(data.shape) == (4, 3)'''),
M(r'''**Read the result:** A shape `(4, 3)` means 4 rows and 3 columns; `numel()` returns **12** because 4 × 3 = 12. The individual data values have not changed—only the way we grouped them determines the shape.

## 2. What is a tensor?

A **tensor** is an array of values organized along one or more **axes** (directions). A scalar is a single number; a vector is a one-dimensional array; a matrix is a two-dimensional array. In PyTorch, all three are tensors.

- **Scalar:** one quiz score, `5`; shape `()` (zero axes).
- **Vector:** four scores, `[3, 5, 7, 9]`; shape `(4,)` (one axis).
- **Matrix:** all the numerical observations; shape `(4, 3)` (two axes).
- **Higher-dimensional tensor:** a group of color images can be organized as `(number_of_images, color_channels, height, width)`.

Think of an **axis** as a direction you can move through the data: down the rows (axis 0) or across the columns (axis 1).'''),
pic('02-tensor-shapes.png','A scalar, a four-number vector, and a 2 × 3 matrix with every cell shown'),
C(r'''scalar = torch.tensor(5.)
vector = torch.tensor([3., 5., 7., 9.])
matrix = torch.tensor([[1., 2., 3.], [4., 5., 6.]])

for label, tensor in [('scalar', scalar), ('vector', vector), ('matrix', matrix)]:
    print(f'{label:6}: shape={tuple(tensor.shape)}, dimensions={tensor.ndim}')

# Reshaping changes the arrangement, not the individual values.
sequence = torch.arange(12)
print('Reshaped to 3 rows × 4 columns:\n', sequence.reshape(3, 4))'''),
M(r'''**Predict before running:** `torch.arange(12)` contains 12 numbers, starting at 0 and ending at 11. If we reshape it to `(3, 4)`, we get 3 rows of 4 numbers—not 12 new numbers. A reshape only works when the total number of entries is preserved.

## 3. Finding a particular value: indexing and slicing

Python starts counting positions at **0**, not 1. `data[1, 2]` means **second row, third column**. That is Ben’s score, `5`.

A colon (`:`) says “take all entries along this axis.” So `data[:, 0]` returns **the first column for every learner**. A slice like `data[0:2]` returns rows at positions 0 and 1, stopping *before* 2.'''),
pic('03-indexing.png','A rectangular tensor with explicit zero-based row and column indices and one highlighted entry'),
C(r'''print('One cell:', data[1, 2].item())
print('All study hours:', data[:, 0].tolist())
print('Ben’s entire row:', data[1].tolist())
print('First two learners:\n', data[0:2])

assert data[1, 2].item() == 5
assert data[:, 0].tolist() == [1., 2., 3., 4.]'''),
M(r'''## 4. Operations: elementwise vs. broadcasting

When two tensors have **the same shape**, an operation like `+` or `*` usually acts on **matching cells**. For example, `[1, 2] + [10, 20]` gives `[11, 22]`.

But what if you have a **column** of 3 numbers and a **row** of 2 numbers? PyTorch can often reuse entries along an axis of length 1. This is called **broadcasting**.

Read the picture **row by row**. For example, the top-right result cell is `1 + 20 = 21`; the bottom-left result cell is `3 + 10 = 13`. There are 3 rows and 2 columns in the result; no cell is left unspecified.'''),
pic('04-broadcasting.png','A complete 3 × 1 plus 1 × 2 broadcasting calculation with a full 3 × 2 result table'),
C(r'''A = torch.tensor([[1.], [2.], [3.]])   # three rows, one column
B = torch.tensor([[10., 20.]])           # one row, two columns

result = A + B
print('A shape:', tuple(A.shape))
print('B shape:', tuple(B.shape))
print('Result shape:', tuple(result.shape))
print(result)

assert result.tolist() == [[11., 21.], [12., 22.], [13., 23.]]'''),
M(r'''**Important distinction:** Broadcasting does **not** mean any two arbitrary shapes are compatible. For aligned axes, the lengths must match **or one of them must be 1**. For example, `(3, 2)` + `(3, 2)` works; `(3, 1)` + `(1, 2)` works; `(3, 2)` + `(4, 2)` does *not* work.

Also, `A * B` is **elementwise multiplication** (with broadcasting when applicable), while `A @ B` is **matrix multiplication**, a different operation we will study in Lesson 2.3.

## 5. Why this matters for machine learning

A learning model processes many examples at once. Rather than looping through every learner and every feature, tensor operations can apply calculations efficiently to the entire data structure. We will use these same ideas later for neural-network inputs, weights and activations.

### Mini-experiment: change just one number'''),
C(r'''experiment = data.clone()  # we create a copy, leaving the original unchanged
experiment[1, 2] = 6.
print('Old Ben score:', data[1, 2].item())
print('Edited Ben score:', experiment[1, 2].item())
print('The edited copy differs from the original:', not torch.equal(data, experiment))  # True'''),
M(r'''### Check your understanding (answer before revealing by running)

1. A tensor has shape `(5, 4)`. How many **rows**, **columns**, and **values** are there?
2. Which expression selects Chika’s **hours** from `data`?
3. What is the result shape of `(2, 1)` + `(1, 3)`? What are the result’s dimensions?
4. Explain **in one sentence** why `*` is not the same as `@`.

**Practice cell:** Try `data[2, 0]`, `data[:, 1]`, and a broadcast of `[[5], [6]] + [[0, 10, 20]]`.

**Takeaway:** The value of a number and the *position* it occupies in a tensor are different ideas. Understanding shape and indexing prevents many later ML errors.

➡️ **Next:** [2.2 Data preprocessing](02-data-preprocessing.ipynb) — real tables often include missing values and categories.'''),
C(r'''# Your turn — edit these expressions and predict their outputs.
print('Chika’s hours:', data[2, 0].item())
print('All practice values:', data[:, 1].tolist())
print('Broadcast example:\n', torch.tensor([[5], [6]]) + torch.tensor([[0, 10, 20]]))''',tags=['exercise'])
]
mkbook(1,'01-data-manipulation-and-tensors.ipynb','Data manipulation and tensors',lesson1)

lesson2=[
M(r'''# 2.2 · Data preprocessing: from messy to usable

**Estimated time:** 30–40 minutes · **Prerequisite:** Lesson 2.1 (rows, columns and tensors).

### What you will learn

- Explain why a dataset may not be ready for machine learning, even when it looks like a table.
- Identify **missing values** and choose a simple method for handling them.
- Separate **features** (inputs) from the **target** (the answer we want to predict).
- Turn category labels into numbers using **one-hot encoding**, then convert the result into a PyTorch tensor.

We continue with our fictional study dataset. This time, imagine Ben forgot to record the number of practice questions. We have also recorded *how* each learner studied (Video or Text), which is a word rather than a number.'''),
M(r'''## 1. Why cleaning comes before modeling

A computer needs a consistent representation: values must be in the right columns, missing information must have an explicit treatment, and categorical labels must be encoded appropriately. The picture below shows the transformation we will complete in this notebook.'''),
pic('05-cleaning-pipeline.png','Three stages: a raw table, cleaned numeric features, and a numerical tensor'),
M(r'''Our starting records are:

| Learner | Hours | Practice | Method | Score / 10 |
|:--|--:|--:|:--|--:|
| Alice | 1 | 2 | Video | 3 |
| Ben | 2 | **missing** | Text | 5 |
| Chika | 3 | 6 | Video | 7 |
| Dara | 4 | 8 | Text | 9 |

A missing value is **not** the same as zero: zero would mean Ben completed *no* practice questions; “missing” means we **do not know**. We must not silently change one into the other.'''),
C(r'''import pandas as pd
import torch
from IPython.display import display

raw = pd.DataFrame({
    'Learner': ['Alice', 'Ben', 'Chika', 'Dara'],
    'Hours': [1., 2., 3., 4.],
    'Practice': [2., None, 6., 8.],
    'Method': ['Video', 'Text', 'Video', 'Text'],
    'Score': [3., 5., 7., 9.],
})
display(raw)
print('Missing values per column:\n', raw.isna().sum())'''),
M(r'''**What did we observe?** `pandas` displays the missing practice value as `NaN` (“Not a Number”). `raw.isna().sum()` counts missing cells in each column. Here, exactly one Practice value is missing.

## 2. Handling a missing value

There is no universally correct replacement. Common choices are:

- **Drop a row** if it cannot be used, though this loses data and can introduce bias.
- **Fill with a meaningful known value** if you really have one.
- **Fill using an observed statistic** such as a median or mean (a simple baseline, not a magic fix).

For demonstration, we fill Ben's practice count using the **mean of the three observed values**:

\[(2+6+8)/3 = 16/3 \approx 5.33.\]

The result is an *estimate*. It is **not** a claim that Ben actually completed 5.33 questions. In a real project, we should record which values were originally missing and evaluate the choice.'''),
pic('06-missing-values.png','The same four-row table before and after the missing practice value is filled with the observed mean'),
C(r'''cleaned = raw.copy()
observed_mean = cleaned['Practice'].mean()  # NaN is ignored by pandas.mean()
cleaned['Practice'] = cleaned['Practice'].fillna(observed_mean)
print('Observed mean:', round(observed_mean, 2))
display(cleaned)
assert cleaned['Practice'].isna().sum() == 0'''),
M(r'''**Important for later:** When splitting real data into training and test sets, compute your fill value using **training data only**, then apply that same value to validation/test data. Otherwise information from the test set leaks into model preparation. We'll formalize this in Chapter 3.

## 3. Decide what the model sees—and what it should predict

**Features** are pieces of information given to the model, such as Hours, Practice and Method. The **target** is the desired answer: Score.

We must not accidentally include Score among the model's features while asking it to predict Score—that would give away the answer. We also exclude the learner's name: it is an identifier, not a numeric explanation of performance.'''),
pic('07-feature-target.png','Inputs enter the model; predictions are compared with separately observed target scores, with each table fully labeled'),
M(r'''**In the illustration**, the predicted scores `[4, 5, 6, 8]` are hypothetical model outputs. They are not known targets. The known scores `[3, 5, 7, 9]` are the targets we compare those predictions against to measure error.'''),
C(r'''features = cleaned[['Hours', 'Practice', 'Method']].copy()
target = cleaned['Score'].copy()
print('Features:')
display(features)
print('Target values:', target.to_list())'''),
M(r'''## 4. Turning categories into numbers

If Method can be `Video` or `Text`, why not replace those with 1 and 2? Because such numbers may wrongly suggest that “Text is twice Video” or that the categories have an order.

**One-hot encoding** makes a separate column for each category. `Video` becomes `[1, 0]`; `Text` becomes `[0, 1]`. The resulting values only say whether a category applies.

For a beginner exercise we keep **both** indicator columns so the transformation is visible. Some models drop one redundant indicator column; that detail can wait until later.'''),
pic('08-one-hot-encoding.png','A fully labeled four-row table showing categorical labels converted to two binary indicator columns'),
C(r'''numeric_features = pd.get_dummies(features, columns=['Method'], dtype=int)
display(numeric_features)
print('Column names:', numeric_features.columns.to_list())
assert numeric_features.select_dtypes(include='object').empty'''),
M(r'''## 5. Ready for PyTorch

We can now convert the numeric feature table to a **tensor**. The model would see four rows (learners) and four columns (Hours, Practice, Method_Text, Method_Video): shape **(4, 4)**. The target contains one score per learner: shape **(4,)**.

The `float32` type is widely used for deep-learning calculations. The code below keeps the **inputs and targets separate**.'''),
C(r'''X = torch.tensor(numeric_features.to_numpy(dtype='float32'))
y = torch.tensor(target.to_numpy(dtype='float32'))

print('Feature columns:', list(numeric_features.columns))
print('X shape:', tuple(X.shape))
print('y shape:', tuple(y.shape))
print('First learner’s features:', X[0].tolist())
print('First learner’s score:', y[0].item())
assert tuple(X.shape) == (4, 4) and tuple(y.shape) == (4,)'''),
M(r'''## 6. A first look at scaling

Some numerical features may have very different magnitudes: study hours might range from 1 to 4, while practice questions might range from 0 to 1,000. In many models, large numerical scales can make optimization harder.

One simple technique is **min–max scaling**: subtract the minimum, then divide by the range. For `[1, 2, 3, 4]`, this produces `[0, 0.333…, 0.667…, 1]`. Scaling changes how a number is represented, not which learner it belongs to.

In real training pipelines, just as with filling missing data, learn scaling parameters from **training data only**.'''),
C(r'''study_hours = torch.tensor([1., 2., 3., 4.])
scaled_hours = (study_hours - study_hours.min()) / (study_hours.max() - study_hours.min())
print('Before:', study_hours.tolist())
print('After :', [round(v, 3) for v in scaled_hours.tolist()])'''),
M(r'''## 7. Practice: explain every column

Before running the next cell, answer:

1. Which part of our table is the **target**, and why should it not be part of `X`?
2. If `Practice` is missing, is it correct to replace it with `0` automatically? Explain.
3. How many feature columns remain if Method has two categories and we keep both indicator columns?
4. Why is filling missing values using statistics from the **test data** a problem?

**Takeaway:** Preprocessing is the step where raw observations become consistent, model-readable **features and targets**. Decisions here affect everything the model learns.

➡️ **Next:** [2.3 Linear algebra](03-linear-algebra.ipynb) — how models combine those numeric features.'''),
C(r'''# Try changing the category encoding: What if a new method "Audio" appeared?
toy = pd.DataFrame({'Method': ['Video', 'Text', 'Audio', 'Video']})
display(pd.get_dummies(toy, dtype=int))
print('Three categories produce three columns with this full one-hot encoding.')''',tags=['exercise'])
]
mkbook(2,'02-data-preprocessing.ipynb','Data preprocessing',lesson2)

lesson3=[
M(r'''# 2.3 · Linear algebra: how a model combines numbers

**Estimated time:** 40–50 minutes · **Prerequisite:** Lesson 2.1 (tensors and shape).

### By the end, you should be able to

- Distinguish a **scalar**, **vector**, **matrix**, and their shapes.
- Calculate a **dot product** by hand and interpret it as a weighted sum.
- Explain a **matrix–vector product**: one prediction per example.
- Explain the shape rule for **matrix multiplication**, and distinguish it from elementwise multiplication.
- Understand **sum**, **mean**, and the **L2 norm** without memorizing formal proofs.

**Running example:** We will use Hours from the fictional learner table to calculate made-up quiz predictions. We deliberately choose a simple rule so each result can be checked by hand.'''),
M(r'''## 1. Why linear algebra matters to machine learning

Imagine predicting a quiz score from study hours. A simple model could follow the rule:

\[\widehat{\text{Score}} = 2\times \text{Hours} + 1.\]

The **2** is the weight for Hours; the **1** is a bias (constant offset). A larger neural network uses the same essential idea—combine many inputs with learned weights—repeated across many layers.

A convenient way to represent this small example is with two **features** per learner: the number of hours and a constant `1` for the bias. The weights are `[2, 1]`.'''),
M(r'''## 2. The dot product: one weighted sum

For two vectors of equal length, the **dot product** multiplies matching entries and **adds the products**. Given `x = [2, 4]` and `w = [3, 1]`:

\[x\cdot w = 2\times3 + 4\times1 = 10.\]

Think: each feature contributes its value multiplied by its weight. The final sum is one number (a scalar).'''),
pic('09-dot-product.png','A dot product with two explicitly labeled vectors and the full 2×3 + 4×1 calculation'),
C(r'''import torch

x = torch.tensor([2., 4.])
w = torch.tensor([3., 1.])

manual = x[0]*w[0] + x[1]*w[1]
print('Hand-style calculation:', manual.item())
print('PyTorch dot:', torch.dot(x,w).item())
assert torch.dot(x,w).item() == 10.'''),
M(r'''**Do not confuse `dot` with elementwise multiplication.** `x*w` returns `[6, 4]`, still a vector. `torch.dot(x,w)` **adds** those two values to return the scalar `10`.

A dot product is a building block of predictions, attention scores in Transformers, and many other neural-network operations.'''),
C(r'''print('Elementwise x*w:', (x*w).tolist())
print('Dot product x·w:', torch.dot(x,w).item())'''),
M(r'''## 3. Matrix–vector multiplication: several predictions at once

Instead of predicting one learner at a time, stack the feature vectors as rows of a matrix. Our four learners have Hours `[1,2,3,4]`. For each learner, we append a constant `1`, because the rule includes a bias.

\[
X = \begin{bmatrix}1&1\\2&1\\3&1\\4&1\end{bmatrix},\quad
w=\begin{bmatrix}2\\1\end{bmatrix},\quad
Xw=\begin{bmatrix}3\\5\\7\\9\end{bmatrix}.
\]

Every **output value** is a **row of X dot w**. The first learner gets `1×2 + 1×1 = 3`, the second `2×2 + 1×1 = 5`, and so on.

**Shape rule:** `(4, 2) @ (2, 1) → (4, 1)`. The **inner dimensions** (both 2) must match, and the **outer dimensions** (4 and 1) give the output shape.'''),
pic('10-matrix-vector.png','A 4 × 2 feature matrix times a 2 × 1 weight vector producing all four predictions in a 4 × 1 output grid'),
C(r'''X = torch.tensor([[1.,1.], [2.,1.], [3.,1.], [4.,1.]])
weights = torch.tensor([[2.], [1.]])
predictions = X @ weights
print('X shape:',tuple(X.shape))
print('Weights shape:',tuple(weights.shape))
print('Predictions shape:',tuple(predictions.shape))
print('Predicted scores:',predictions.squeeze(1).tolist())
assert predictions.squeeze(1).tolist() == [3.,5.,7.,9.]'''),
M(r'''## 4. Matrix–matrix multiplication: what changes?

The same rule works when the second operand is a *matrix* rather than one weight vector. If `A` has shape `(2, 3)` and `B` has shape `(3, 2)`, their product has shape `(2, 2)`.

To find **one output cell**, take a row from `A` and a column from `B` and calculate their dot product. The top-left output, for example, is `1×1 + 2×0 + 3×1 = 4`. The diagram below includes **every** input and output cell. Check another output cell yourself.'''),
pic('11-matrix-matrix.png','Fully labeled 2 × 3 and 3 × 2 matrices with a complete 2 × 2 result and an annotated cell calculation'),
C(r'''A = torch.tensor([[1.,2.,3.],[4.,5.,6.]])
B = torch.tensor([[1.,0.],[0.,1.],[1.,1.]])
C_result = A @ B
print(C_result)
print('Result shape:',tuple(C_result.shape))
assert C_result.tolist() == [[4.,5.],[10.,11.]]'''),
M(r'''### Three symbols to remember

| Python expression | Meaning | Example result |
|:--|:--|:--|
| `a + b` | add matching entries (or broadcast) | `[1,2]+[3,4] → [4,6]` |
| `a * b` | multiply matching entries (or broadcast) | `[1,2]*[3,4] → [3,8]` |
| `A @ B` | row–column dot products | `(2,3)@(3,2) → (2,2)` |

This distinction becomes critical when reading neural-network formulas like `X @ W + b`.

## 5. Reductions: turning many values into fewer values

A **reduction** summarizes a collection. `sum()` adds; `mean()` averages. Along `axis=0`, we summarize **down the rows**, getting one value per column. Along `axis=1`, we summarize **across columns**, getting one value per row.

For the matrix `[[1,2],[3,4]]`, column sums are `[4,6]`; row sums are `[3,7]`.
'''),
C(r'''small = torch.tensor([[1., 2.], [3., 4.]])
print('All entries sum:', small.sum().item())
print('Column sums (dim=0):', small.sum(dim=0).tolist())
print('Row sums (dim=1):', small.sum(dim=1).tolist())
print('Mean of all entries:',small.mean().item())'''),
M(r'''## 6. Norms: measuring vector size

The **L2 norm** measures a vector's length. For `v = [3, 4]`, picture a right triangle with horizontal side 3 and vertical side 4. Pythagoras tells us the diagonal has length 5.

\[\|v\|_2=\sqrt{3^2+4^2}=5.\]

This matters because we often want to measure the size of a parameter vector, error vector, or gradient. You do not need advanced geometry to recognize what a norm tells you.'''),
pic('12-vector-norm.png','A 3–4–5 right triangle illustrating the length of a vector with entries 3 and 4'),
C(r'''v = torch.tensor([3.,4.])
print('L2 norm:', torch.linalg.vector_norm(v).item())
print('Squared entries:',(v*v).tolist())
assert torch.linalg.vector_norm(v).item() == 5.'''),
M(r'''## 7. Small experiment: change one weight

Our simple predictor uses `[weight_for_hours, bias] = [2,1]`. What if the Hours weight becomes **3**? Higher hours would have more effect on the prediction, because they are multiplied by a larger number.

Try predicting the four scores **before** running the cell. (They will no longer match the original synthetic targets; that is useful to notice.)'''),
C(r'''new_weights = torch.tensor([[3.],[1.]])
changed_predictions = X @ new_weights
print('Previous:',predictions.squeeze().tolist())
print('New:',changed_predictions.squeeze().tolist())''',tags=['exercise']),
M(r'''### Check your understanding

1. Calculate `[3, 2] · [2, 5]` by hand. Is the result a number or a vector?
2. What output shape should you expect from `(5, 3) @ (3, 2)`? Why?
3. When is `A * B` **not** the same as `A @ B`?
4. What is the L2 norm of `[0, 6, 8]`?
5. In the prediction `2×Hours + 1`, which part is the **bias**?

**Takeaway:** Linear algebra lets models combine many numerical features using weighted sums, while tensor shape tells us exactly which calculations are valid.

➡️ **Next:** [2.4 Calculus and automatic differentiation](04-calculus-and-autograd.ipynb) — how does the model know which weight to change?''')
]
mkbook(3,'03-linear-algebra.ipynb','Linear algebra',lesson3)

lesson4=[
M(r'''# 2.4 · Calculus and automatic differentiation

**Estimated time:** 45–55 minutes · **Prerequisite:** Lesson 2.3 (a weight, a prediction, and an error).

### What you will understand by the end

- A **derivative** describes how an output changes when an input changes.
- A **gradient** collects partial derivatives for several adjustable parameters.
- The **chain rule** tells us how changes flow through a sequence of calculations.
- A **forward pass** computes a prediction and loss; a **backward pass** computes gradients.
- PyTorch **autograd** computes the derivatives that we would otherwise calculate by hand.

**Our continuous example:** A learner studied `x = 2` hours and the target score is `5`. The toy model predicts `ŷ = w×x + b`, where we start with `w = 1`, `b = 1`.

The example intentionally uses one weight and one training point so you can check **every number**. A real model typically has many parameters and examples.'''),
M(r'''## 1. Derivatives: how sensitive is an output?

Start with the simple rule `f(x) = x²`.

At `x = 2`, the output is `f(2) = 4`. If we increase x a little, the output rises. A **derivative** measures the rate of change *at a particular input*. Geometrically, it is the slope of the tangent line to the curve.

For this rule, `f′(x) = 2x`. At `x = 2`, the derivative is **4**. That means a tiny increase of `0.01` in x changes f by roughly `4×0.01 = 0.04` near that point.

**The derivative is not the output.** At x=2 the output is 4 and the slope is also 4, but that numerical coincidence is specific to this example.'''),
pic('13-derivative-tangent.png','The curve f(x)=x² and its tangent at x=2, highlighting that the derivative is its local slope'),
C(r'''import torch

# Approximate the derivative from a small change in x.
def f(x):
    return x**2

x = 2.0
for h in [0.1, 0.01, 0.001]:
    approximate_derivative = (f(x+h)-f(x))/h
    print(f'h={h:5g} → approximate slope={approximate_derivative:.3f}')
print('Exact slope from 2*x:', 2*x)'''),
M(r'''As **h gets smaller**, the measured slope approaches 4. This is the idea behind the limit definition of a derivative. You do not need to derive all the calculus rules here; understanding what they *measure* is the important first step.

## 2. Partial derivatives and gradients

A prediction usually depends on several quantities, such as **weight `w`** and **bias `b`**. A **partial derivative** tells us how the result changes when one of these is changed while the others are held fixed.

For `ŷ = w×x + b`, treating x as a given input:

- `∂ŷ/∂w = x`: how the prediction changes with the weight.
- `∂ŷ/∂b = 1`: how the prediction changes with the bias.

If a loss depends on many parameters, we collect the partial derivatives into a **gradient**: `[∂L/∂w, ∂L/∂b, …]`. Each number tells us which way the loss would change if we adjusted its corresponding parameter.

## 3. First do the forward calculation

We want a prediction close to the target `5`. With `x=2`, `w=1` and `b=1`:

1. **Prediction:** `ŷ = 1×2 + 1 = 3`.
2. **Difference:** `ŷ - target = 3 - 5 = -2`.
3. **Squared-error loss:** `L = (-2)² = 4`.

A **loss function** converts the model's prediction error into a number that training tries to reduce. This simple squared error is not the only possible loss, but it makes the arithmetic easy to inspect.'''),
pic('14-forward-graph.png','Four connected stages of a forward pass: input, prediction, difference, and squared error'),
C(r'''hours = torch.tensor(2.)
target = torch.tensor(5.)
w = torch.tensor(1., requires_grad=True)
b = torch.tensor(1., requires_grad=True)

prediction = w*hours + b
loss = (prediction - target)**2

print('Prediction:',prediction.item())
print('Squared error:',loss.item())
print('Gradient BEFORE backward:',w.grad)
assert prediction.item()==3. and loss.item()==4.'''),
M(r'''Notice that `w.grad` is `None` here. The **forward pass** calculates the **value** of the prediction and loss, but it has not yet calculated the derivatives. PyTorch records operations involving `requires_grad=True` tensors so it can differentiate them later.

## 4. The chain rule explains the backward calculation

Our loss depends on `w` **through** the prediction:

\[w\;\longrightarrow\;\hat y = 2w+1\;\longrightarrow\;L=(\hat y-5)^2.\]

The **chain rule** says: multiply the slope of the loss with respect to the prediction by the slope of the prediction with respect to the weight:

\[\frac{dL}{dw} = \frac{dL}{d\hat y}\times\frac{d\hat y}{dw}.\]

At the starting point:

- `dL/dŷ = 2(ŷ - 5) = 2(3 - 5) = -4`.
- `dŷ/dw = x = 2`.
- So **`dL/dw = -4 × 2 = -8`**.

For bias, the slope is `dŷ/db = 1`, so `dL/db = -4 × 1 = -4`.

A *negative* derivative with respect to w means that **a small increase in w** would initially **reduce** the loss.'''),
pic('15-backward-chain-rule.png','The chain rule calculation leading to gradient −8 and a weight update from 1 to 1.8'),
C(r'''loss.backward()  # run automatic differentiation
print('dL/dw:',w.grad.item())
print('dL/db:',b.grad.item())
assert w.grad.item()==-8.0
assert b.grad.item()==-4.0'''),
M(r'''### What did `backward()` actually do?

It **computed derivatives** and stored them in `.grad`. It did **not** update `w` or `b`. In neural-network training, computing gradients (backpropagation) and **using** those gradients to change parameters (optimization) are separate steps.

**One controlled update:** To see the effect of a gradient without changing two parameters simultaneously, we will update **only the weight** with learning rate `0.1`, holding b fixed at 1.

\[w_{new} = w_{old} - 0.1\frac{dL}{dw} = 1 - 0.1(-8) = 1.8.\]

A **learning rate** controls how large a step we take. The updated prediction is `2×1.8 + 1 = 4.6`, and squared error is `(4.6-5)² = 0.16`—smaller than 4.'''),
pic('16-gradient-step.png','The loss curve showing how updating the weight from 1.0 to 1.8 reduces squared error from 4 to 0.16'),
C(r'''learning_rate = 0.1
with torch.no_grad():  # this is an update, not a step we want to differentiate
    w -= learning_rate*w.grad

new_prediction = w*hours + b
new_loss = (new_prediction - target)**2
print('New weight:',round(w.item(),3))
print('New prediction:',round(new_prediction.item(),3))
print('New loss:',round(new_loss.item(),4))
assert abs(new_loss.item() - 0.16) < 1e-5'''),
M(r'''## 5. Why gradients need to be cleared

By default, PyTorch **accumulates** gradients into `.grad`: calling backward a second time can **add** derivatives rather than replacing the old ones. Training loops therefore typically clear gradients before the next backward pass (for example `optimizer.zero_grad()` or `w.grad.zero_()`).

The small demonstration below creates a **fresh weight** to avoid confusing its derivative with any previous calculation.'''),
C(r'''fresh_w = torch.tensor(1.,requires_grad=True)
first_loss = (2*fresh_w + 1 - 5)**2
first_loss.backward()
print('First gradient:',fresh_w.grad.item())

fresh_w.grad.zero_()
second_loss = (2*fresh_w + 1 - 5)**2
second_loss.backward()
print('After clearing, second gradient:',fresh_w.grad.item())'''),
M(r'''## 6. Commonly confused terms

| Term | What it means | What it **does not** mean |
|:--|:--|:--|
| **Forward propagation** | The model calculates its prediction (and loss) from current inputs/parameters. | It is not a parameter update. |
| **Automatic differentiation (autograd)** | Software calculates derivatives of code operations. | It is not the optimizer itself. |
| **Backpropagation** | A reverse pass applies the chain rule to calculate gradients of a loss with respect to parameters. | It does not automatically update weights. |
| **Gradient descent** | A procedure uses a gradient to change parameters, usually toward lower loss. | It is not the derivative calculation itself. |

**Forward-mode automatic differentiation** is another method for computing derivatives. It is **not the same thing** as “forward propagation.” We do not need forward-mode details for this beginner lesson.

## 7. Your turn: predict the derivative

If `L = (2w + 1 - 5)²`, what is `dL/dw` at `w = 2`? Check by hand **before** running the following cell. What does the derivative tell you about where the minimum might be?'''),
C(r'''test_w = torch.tensor(2.,requires_grad=True)
test_loss = (2*test_w + 1 - 5)**2
test_loss.backward()
print('Loss at w=2:',test_loss.item())
print('Gradient at w=2:',test_w.grad.item())''',tags=['exercise']),
M(r'''### Check your understanding

1. Is a derivative the output of the function or the output's *rate of change*?
2. In the toy example, why is `w.grad` initially `None`?
3. What are the two multiplications involved in the **chain rule** that give `dL/dw = -8`?
4. Why do we write `with torch.no_grad():` around the manual update?
5. Does `.backward()` change parameters directly? If not, what changes them?

**Takeaway:** Training a model involves calculating a loss, finding how sensitive it is to the parameters (gradients), and applying updates that aim to reduce that loss. This is the beginning of **backpropagation**, the mechanism used to train neural networks.

➡️ **Next:** [2.5 Probability and statistics](05-probability-and-statistics.ipynb) — why individual outcomes and datasets are uncertain.''')
]
mkbook(4,'04-calculus-and-autograd.ipynb','Calculus and autograd',lesson4)

lesson5=[
M(r'''# 2.5 · Probability and statistics: reasoning about uncertainty

**Estimated time:** 35–45 minutes · **Prerequisite:** counting, fractions and running simple Python code.

### By the end, you should be able to

- Explain a **random experiment**, an **outcome**, and an **event**.
- Interpret **probability** as a number between 0 and 1.
- Compare **theoretical probability** with **observed relative frequency**.
- See why estimates become more stable as sample sizes grow (without expecting them to be perfectly equal).
- Compute a simple **conditional probability** and basic summaries such as the mean.

We first use coin tosses because we know the ideal mathematical probabilities. Then we return to our **four fictional learners** and show why tiny datasets require caution.'''),
M(r'''## 1. Probability is about uncertain outcomes

Toss a fair coin. There are two possible outcomes: **Heads (H)** and **Tails (T)**. A fair coin assigns each outcome probability `1/2 = 0.5 = 50%`.

An **event** is a set of outcomes we care about. If we toss a coin *twice*, the four equally likely outcomes are HH, HT, TH and TT. The event “exactly one head” includes **HT and TH**, so:

\[P(\text{exactly one head}) = 1/4 + 1/4 = 1/2.\]

These calculations assume **fair and independent** tosses. If the coin is biased, the probabilities change.'''),
pic('17-coin-outcomes.png','A two-toss probability tree showing all four outcomes and probability one-quarter for each'),
M(r'''**Interpretation:** A probability of `0.5` does not promise that the first 10 tosses will produce *exactly* five heads. It describes the long-run behavior of the ideal random process, not a guaranteed count in a small sample.

## 2. Observed frequency is an estimate

We can *simulate* tossing a fair coin. Each trial produces either `0` (tails) or `1` (heads). The **relative frequency** of heads is:

\[\frac{\text{number of observed heads}}{\text{total tosses}}.\]

This is an **estimate** from the results we observed. It need not equal the theoretical probability exactly, even with many tosses.

We use a fixed random seed so the outputs are reproducible on different learners' machines.'''),
C(r'''import numpy as np
import torch
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
tosses = rng.integers(0,2,size=1000)  # 0 = tails, 1 = heads

for n in [10,100,1000]:
    heads = int(tosses[:n].sum())
    print(f'First {n:4} tosses: {heads:4} heads; fraction = {heads/n:.3f}')'''),
M(r'''Now look at the **complete running estimate**, not just the three snapshots. The orange line shows the theoretical probability 0.5, while the teal line records the fraction observed as we collect more tosses.'''),
pic('18-sample-size.png','A reproducible plot of the running observed fraction of heads across 1000 simulated coin tosses, with a 0.5 reference line'),
C(r'''running_fraction = np.cumsum(tosses) / np.arange(1,len(tosses)+1)
fig,ax=plt.subplots(figsize=(8,3.7))
ax.plot(np.arange(1,len(tosses)+1),running_fraction,label='Observed fraction')
ax.axhline(.5,linestyle='--',label='Fair coin probability (0.5)')
ax.set(xlabel='Toss count',ylabel='Fraction of heads',title='Try changing the random seed or number of tosses')
ax.legend();plt.show()'''),
M(r'''### What larger samples really mean

Larger samples **usually** make an empirical proportion more stable, because a few unusual outcomes have less influence. This is an example of the **law of large numbers**. However:

- The proportions do **not** become exactly equal to 0.5 after a fixed number of tosses.
- The actual **counts** of heads and tails do **not** need to be equal.
- The process must be appropriate for the assumptions: a biased coin will stabilize around its own probability, not 0.5.

This matters in ML because a model's evaluation score on a **small test set** can be noisy.'''),
M(r'''## 3. A conditional probability asks a more specific question

Return to the toy class:

| Learner | Hours | Score | Passed (score ≥ 6)? |
|:--|--:|--:|:--|
| Alice | 1 | 3 | No |
| Ben | 2 | 5 | No |
| Chika | 3 | 7 | Yes |
| Dara | 4 | 9 | Yes |

Across all four learners, the **observed fraction** who passed is `2/4 = 0.5`. But perhaps we ask: **Among learners who studied at least 3 hours, what fraction passed?**

Only Chika and Dara are in that group, and both passed. So **`P(pass | Hours ≥ 3)`**, as *estimated from this toy sample*, is `2/2 = 1.0`.

The vertical bar `|` reads **“given that.”** It restricts which rows we count in the denominator.'''),
pic('19-conditional-probability.png','A fully labeled count table for pass versus not pass grouped by study hours, including row/column totals'),
C(r'''import pandas as pd

sample = pd.DataFrame({
    'Learner':['Alice','Ben','Chika','Dara'],
    'Hours':[1,2,3,4],
    'Score':[3,5,7,9],
})
sample['Passed'] = sample['Score']>=6
sample['Hours_3_or_more'] = sample['Hours']>=3

print('Overall pass fraction:',sample['Passed'].mean())
print('Pass fraction given Hours>=3:',
      sample.loc[sample['Hours_3_or_more'],'Passed'].mean())
print('\nCounts:\n',pd.crosstab(sample['Passed'],sample['Hours_3_or_more'],margins=True))'''),
M(r'''**Critical caution:** These are only **four invented observations**. The conditional estimate `1.0` is not a law about students, a reliable estimate for the wider world, or proof that studying three hours *causes* a pass. Statistical relationships can reflect other differences between groups. The difference between **observation** and **causal explanation** will matter in later ML and AI safety evaluation.

## 4. Mean and spread: two basic statistical summaries

A **mean** (average) tells us the center of a group of numbers. For our scores `[3,5,7,9]`, the mean is `(3+5+7+9)/4 = 6`.

But the mean hides **variation**: learners scored differently. Standard deviation gives one way to summarize **spread**. For this beginner course, you only need to understand that a larger standard deviation usually means the values vary more around the mean. We'll use PyTorch to calculate it.

Be careful when interpreting a statistic: a single mean or pass rate is not a complete description of a dataset.'''),
C(r'''scores = torch.tensor([3.,5.,7.,9.])
print('Average score:',scores.mean().item())
print('Minimum and maximum:',scores.min().item(),scores.max().item())
print('Population standard deviation:',round(scores.std(unbiased=False).item(),3))

second_group=torch.tensor([6.,6.,6.,6.])
print('Another group with same mean:',second_group.mean().item())
print('But different spread:',second_group.std(unbiased=False).item())'''),
M(r'''## 5. Why probability matters for machine learning and AI safety

Models make predictions on imperfect observations, under uncertainty. When evaluating models, we often report fractions such as **accuracy** or **failure rate**. These numbers depend on which examples were tested, how many examples were included, and what we counted as success.

Even if two models have the same accuracy on a tiny set, that alone does not show they have the same reliability across different situations. We need to be able to discuss **sampling, uncertainty, and distribution of outcomes** rather than treating one result as absolute certainty.

The purpose of this lesson is *not* to master all of statistics. It is to develop the habits of asking: “What happened?”, “How often?”, “Among whom?”, and “How confident should we be?”

## 6. Small experiment: compare different random seeds

Re-run the following cell using seed `0`, `1`, and `2`. Do the first 10 flips always have the same fraction of heads? Do the first 1000 fractions become identical?'''),
C(r'''for seed in [0,1,2]:
    flips = np.random.default_rng(seed).integers(0,2,size=1000)
    print(f'seed {seed}: first 10 = {flips[:10].mean():.2f}, all 1000 = {flips.mean():.3f}')''',tags=['exercise']),
M(r'''### Check your understanding

1. What is the difference between theoretical probability and the **fraction observed** in a sample?
2. For two fair independent tosses, what is the probability of **at least one head**?
3. Why should you not expect **exactly** 500 heads in every set of 1,000 fair-coin tosses?
4. What does `P(pass | Hours ≥ 3)` mean—and which learners are in its denominator?
5. Two groups have the same mean score. Does that guarantee that they have the same spread?

**Takeaway:** Probability gives a way to reason about uncertain events; statistics helps us describe the outcomes that actually occurred. Both are essential for interpreting a model's behavior responsibly.

➡️ **Next:** [Chapter 2 checkpoint](quizzes/chapter-02-checkpoint.ipynb). Chapter 3 (Machine Learning Basics) is the next planned chapter.''')
]
mkbook(5,'05-probability-and-statistics.ipynb','Probability and statistics',lesson5)

reference=[
M(r'''# Chapter 2 quick reference · Finding help in Python and PyTorch

You do **not** need to memorize every PyTorch function. Much more important is knowing how to inspect a function and verify what it expects.

- `help(torch.ones)` shows documentation for making a tensor of ones.
- `torch.ones(2, 3)` creates a tensor with **2 rows and 3 columns**.
- `dir(torch)` lists available names, which is useful for discovery but not something to memorize.
- In Jupyter, `torch.sum?` also shows help in an interactive notebook (the standard Python `help(...)` works everywhere).

These examples are adapted in scope from the uploaded D2L **Documentation** notebook.'''),
C(r'''import torch
print('A 2 × 3 tensor of ones:\n',torch.ones(2,3))
print('Shape:',tuple(torch.ones(2,3).shape))
print('Does torch have a mean function?',hasattr(torch,'mean'))'''),
M(r'''## When stuck, check three things

1. **Shape:** What dimensions does the function expect and return?
2. **Type:** Do inputs need to be floats, integers, tensors, or Python lists?
3. **Meaning:** Does the operation act on each element, each row/column, or the entire tensor?

Practise by reading the documentation string rather than copying unfamiliar code blindly.'''),
C(r'''# Prints the first lines of help without overwhelming the notebook.
first_lines = (torch.mean.__doc__ or '').strip().splitlines()[:13]
print('\n'.join(first_lines))'''),
M(r'''## Key terms from Chapter 2

| Term | Plain meaning |
|:--|:--|
| **Tensor** | A regular arrangement of values, with a defined shape. |
| **Feature** | A model input such as study hours. |
| **Target** | The desired prediction (for example a quiz score). |
| **Dot product** | Multiply corresponding vector entries, then add. |
| **Gradient** | Derivatives showing how a loss changes with model parameters. |
| **Autograd** | Automatic calculation of those derivatives. |
| **Probability** | A mathematical way to describe how likely an uncertain event is. |

**Next:** Return to the [Chapter 2 overview](README.md), or complete the [checkpoint](quizzes/chapter-02-checkpoint.ipynb).''')
]
mkbook(6,'06-pytorch-documentation-reference.ipynb','Reference',reference)

checkpoint=[
M(r'''# Chapter 2 checkpoint · Can you explain what the code is doing?

**Estimated time:** 20–30 minutes. Try the questions **before** opening the instructor answers. The point is to understand what the numbers *mean*, not just get Python to run.

This checkpoint covers all five lessons. You can discuss answers aloud or write them beneath each prompt.'''),
M(r'''## A. Tensors and tables

**Q1.** Four learners each have 3 measurements. What is the shape of a numeric tensor holding this table? How many values does it contain?

**Q2.** Given `T = [[1,2,3],[4,5,6]]`, what is `T[1,0]`? Explain why.

**Q3.** Why can a `(3,1)` tensor be added to a `(1,2)` tensor? What is the resulting shape?'''),
C(r'''import torch
T = torch.tensor([[1,2,3],[4,5,6]])
# Write your predictions in a comment, then use this code to check Q2.
print('T[1,0] =',T[1,0].item())''',tags=['exercise']),
M(r'''## B. Preprocessing

**Q4.** A student did not report any practice-question count. Explain the difference between **missing** and **zero**.

**Q5.** Should the model's target score also be included in the input features if we ask the model to predict the score? Why?

**Q6.** Explain one-hot encoding using the categories `Video`, `Text`, and `Audio`.'''),
M(r'''## C. Linear algebra

**Q7.** Calculate `[2,3] · [4,5]` by hand, showing the multiplication and addition.

**Q8.** What is the result shape of a `(4,2)` matrix multiplied by a `(2,3)` matrix? Which dimensions must agree?

**Q9.** Explain in one sentence why `A*B` and `A@B` can produce different results.'''),
C(r'''a = torch.tensor([2.,3.]); b = torch.tensor([4.,5.])
print('Elementwise:',(a*b).tolist())
print('Dot product:',torch.dot(a,b).item())''',tags=['exercise']),
M(r'''## D. Gradients

**Q10.** For `ŷ=2w+1` and target `5`, what are the prediction and squared error when `w=1`?

**Q11.** Why is `dL/dw = -8` at that starting point? Describe the **two derivatives** we multiply.

**Q12.** Does `.backward()` update model weights? What operation must happen afterward?'''),
M(r'''## E. Probability and statistics

**Q13.** For two independent fair coin tosses, what is the probability of **exactly one head**?

**Q14.** If the theoretical chance of heads is 0.5, does that mean **exactly** 50 of 100 tosses must be heads? Why not?

**Q15.** In a table of four students, the two who studied at least 3 hours both passed. Interpret the observed fraction `2/2` and explain why it does *not* prove that 3 hours causes a pass.

### Finish

Pick **one** chapter concept that felt confusing before but that you can now explain using a diagram and a tiny code example. If you still struggle with a concept, repeat the matching lesson before continuing.

*An instructor answer key is available separately in `quizzes/instructor-answer-key.md`.*''')
]
checkpoint_nb=nbf.v4.new_notebook(cells=checkpoint,metadata=base())
nbf.write(checkpoint_nb,ROOT/'quizzes'/'chapter-02-checkpoint.ipynb')
(ROOT/'quizzes'/'instructor-answer-key.md').write_text('''# Chapter 2 checkpoint — Instructor answer key

Keep this file separate from the main learner view until after the checkpoint.

1. `(4, 3)`; 12 numbers.
2. `4`. Index 1 selects the second row; index 0 the first column.
3. An axis with length one can broadcast; the result is `(3, 2)`.
4. “Missing” means unknown; 0 means the true value is zero.
5. No. That would leak the answer into the inputs.
6. Three indicator columns (`is_Video`, `is_Text`, `is_Audio`). Each row has 1 in its category column and 0 in the other two.
7. `2×4 + 3×5 = 8 + 15 = 23`.
8. `(4,3)`. The inner dimensions (2) match.
9. `*` is elementwise multiplication, whereas `@` computes row–column dot products.
10. Prediction `3`; squared error `(3−5)² = 4`.
11. `dL/dŷ = 2(3−5) = −4`, and `dŷ/dw = 2`. Multiply to get `−8`.
12. No. It calculates and stores gradients. An optimizer or manual weight-update step then changes parameters.
13. `2/4 = 1/2`, because HT and TH qualify.
14. No; 50 is an expectation, not a guaranteed observed count. Samples vary.
15. The **sample conditional proportion** is 100% among the two higher-hour learners. Only four synthetic cases exist; correlation is not evidence of a general causal rule.
''',encoding='utf-8')

names=[
'01-data-manipulation-and-tensors.ipynb',
'02-data-preprocessing.ipynb',
'03-linear-algebra.ipynb',
'04-calculus-and-autograd.ipynb',
'05-probability-and-statistics.ipynb',
'06-pytorch-documentation-reference.ipynb']
combined=[]
for i,name in enumerate(names):
    nbf_book=nbf.read(ROOT/name,as_version=4)
    if i:
        combined.append(M('---\n\n*Continue directly into the next lesson below, or open the corresponding individual lesson notebook.*'))
    combined.extend(nbf_book.cells)
combinedbook=nbf.v4.new_notebook(cells=combined,metadata=base())
combinedbook.metadata['fsilearning']['type']='complete-chapter-workbook'
nbf.validate(combinedbook)
nbf.write(combinedbook,ROOT/'00-chapter-02-complete-workbook.ipynb')
print('Combined workbook cells',len(combined))

README='''# Chapter 2 — Math Foundations: Interactive Jupyter Workbooks

**FSI · Machine Learning Foundations for AI Safety (MLFAS)**  
**For:** absolute beginners · **Recommended time:** roughly 4–5 hours including experiments.

## Open the complete workbook

**[`00-chapter-02-complete-workbook.ipynb`](00-chapter-02-complete-workbook.ipynb)** is the complete chapter, in one notebook. It contains explanations, accurately gridded illustrations, live code cells, and exercises **on the same page**. It also includes the short documentation appendix.

### Or follow individual lessons (easier for a learning website)

| Order | Workbook | Main concepts | Illustrations |
|---:|:--|:--|---:|
| 1 | [Data manipulation & tensors](01-data-manipulation-and-tensors.ipynb) | shapes, indexing, broadcasting | 4 |
| 2 | [Data preprocessing](02-data-preprocessing.ipynb) | missing values, features, one-hot encoding, scaling | 4 |
| 3 | [Linear algebra](03-linear-algebra.ipynb) | weighted sums, matrix multiplication, reductions, norms | 4 |
| 4 | [Calculus & autograd](04-calculus-and-autograd.ipynb) | derivatives, chain rule, backpropagation, weight update | 4 |
| 5 | [Probability & statistics](05-probability-and-statistics.ipynb) | fair coin, observed frequency, conditional probability, mean & spread | 3 |
| Appendix | [PyTorch documentation reference](06-pytorch-documentation-reference.ipynb) | finding help & quick vocabulary | — |
| Quiz | [Chapter checkpoint](quizzes/chapter-02-checkpoint.ipynb) | 15 concept checks + practice cells | — |

**Every one of the 19 diagrams is exported as both native vector SVG and high-resolution PNG.** The notebooks prefer SVG using a `<picture>` element and use PNG as the compatibility fallback. Tables use real rectangular row-and-column grids, labeled headers, and one value per cell. The lesson notebooks also use actual `pandas.DataFrame` displays when the table should be manipulated in code. Image files remain editable by rebuilding from `scripts/build_chapter2_jupyter.py` (script supplied separately in the ZIP).

## GitHub folder convention

```text
mlfas/
└── chapter-02-math-foundations/
    ├── 00-chapter-02-complete-workbook.ipynb
    ├── 01-data-manipulation-and-tensors.ipynb
    ├── 02-data-preprocessing.ipynb
    ├── 03-linear-algebra.ipynb
    ├── 04-calculus-and-autograd.ipynb
    ├── 05-probability-and-statistics.ipynb
    ├── 06-pytorch-documentation-reference.ipynb
    ├── images/                      # 19 SVG diagrams + 19 matching PNG fallbacks
    ├── quizzes/
    │   ├── chapter-02-checkpoint.ipynb
    │   └── instructor-answer-key.md
    ├── chapter.json
    ├── requirements.txt
    └── README.md
```

The lessons are **not** separate `.md` files anymore. Their teaching text is in **Markdown cells inside `.ipynb`**, next to diagrams and executable code. Chapter 1 and Chapters 3–6 are not bundled here.

## How learners use it

1. Install Python (3.10+) and JupyterLab, or open the notebooks in a Jupyter-compatible environment.
2. From this chapter folder: `pip install -r requirements.txt`, then `jupyter lab`.
3. Open **the complete workbook** *or* one numbered notebook. Read text and predict outputs before using **Run**.
4. No internet connection, GPU, D2L package, or downloadable training data is needed **after dependencies are installed**.
5. When the lessons are done, complete the checkpoint notebook.

**GitHub display vs. execution:** GitHub can *render* the saved notebook content and static SVG diagrams (or PNG fallback); running code requires a Jupyter kernel (locally or via a hosted notebook runtime). A website can render the `.ipynb` Markdown/cells and link to a notebook runtime for experiments. GitHub alone is not a code-execution backend.


## Illustration strategy — SVG first, PNG fallback

- Both `images/<name>.svg` and `images/<name>.png` are generated from the **same source drawing** by `scripts/build_chapter2_jupyter.py`. Never manually substitute a low-quality PNG inside an `.svg` wrapper.
- Every lesson notebook uses standard HTML `<picture>` with an SVG `<source>` and a PNG `<img>` fallback; it includes descriptive alternate text and a caption. The complete workbook uses the same assets.
- Browser support for `<picture>` with SVG is excellent; notebook renderers may differ. Verify in the **actual** Jupyter/GitHub/website renderer before shipping. For website runtime failures (e.g., SVG network error), the frontend should explicitly change `img.src` to the PNG URL on error; HTML `<picture>` alone does not guarantee a fallback when the SVG request fails.
- For **datasets**, the interactive Pandas or Markdown table is the source of truth. Diagrammatic tables supplement it, with complete column headers, row labels, visible cell borders and a value in every data cell.
- A reproducibility check script at `scripts/validate_assets.py` verifies pairs, true vector SVGs, notebook paths, and the presence of SVG-first references.
- To regenerate locally, install the visualization dependencies and run `python scripts/build_chapter2_jupyter.py` from anywhere. Assets and notebooks regenerate together.

## Instructional design

Each lesson proceeds **explain → fully labeled diagram → annotated computation → runnable code → experiment → check understanding**. The examples are intentionally synthetic and mathematically small. The same four learners appear through tensor creation, preprocessing, matrix prediction, and simple probability. A one-weight toy example bridges algebra and backpropagation.

**Scope adapted from the seven attached Dive into Deep Learning notebooks:** `ndarray.ipynb`, `pandas.ipynb`, `linear-algebra.ipynb`, `calculus.ipynb`, `autograd.ipynb`, `probability.ipynb`, `lookup-api.ipynb`. The source notebooks informed *what to teach*; the prose, examples, questions, and diagram assets in this rebuild were newly authored.

Original learning reference: [Dive into Deep Learning — Chapter 2 (Preliminaries)](https://d2l.ai/chapter_preliminaries/index.html).
'''
(ROOT/'README.md').write_text(README,encoding='utf-8')
(ROOT/'requirements.txt').write_text('jupyterlab>=4,<5\nnbformat>=5,<6\nnbclient>=0.10,<1\ntorch>=2.2,<3\npandas>=2.0,<3\nnumpy>=1.24,<3\nmatplotlib>=3.8,<4\n',encoding='utf-8')
manifest={'chapter':2,'slug':'chapter-02-math-foundations','title':'Mathematical Foundations for Machine Learning','format':'jupyter-notebook','entry':'00-chapter-02-complete-workbook.ipynb','lessons':[],'quiz':'quizzes/chapter-02-checkpoint.ipynb','images':{'preferred':'svg','fallback':'png','count':19}}
for i,f in enumerate(names):
 manifest['lessons'].append({'order':i+1,'title':['Data manipulation and tensors','Data preprocessing','Linear algebra','Calculus and automatic differentiation','Probability and statistics','PyTorch documentation reference'][i], 'path':f,'kind':'reference' if i==5 else 'lesson'})
(ROOT/'chapter.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
