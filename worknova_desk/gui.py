"""Offline desktop review UI. No HTTP, embedding web service, or automatic payments.

Requires a local interactive display and Python's stdlib Tk 8.6; not yet
verified on the target Windows10/11 desktop.
"""
from __future__ import annotations

import argparse
import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, simpledialog, messagebox, filedialog

from .core import Desk, DeskError
from .documents import export_document


def parse_rows(lines: str, *, kind: str) -> list[dict]:
    """Friendly multiline input; one simple service/milestone per row.

    Quotes:  설명|수량|단가(원)
    Milestones: 단계|금액(원)
    """
    if not isinstance(lines, str) or len(lines) > 30000: raise DeskError("too much input")
    result = []
    headers = ("description", "quantity", "unit_krw") if kind == "quote" else ("title", "amount_krw")
    if kind not in ("quote", "milestone"): raise DeskError("invalid row type")
    for no, line in enumerate(lines.strip().splitlines(), start=1):
        if not line.strip(): continue
        cells = [x.strip() for x in line.split("|")]
        if len(cells) != len(headers): raise DeskError(f"{no}행: 구분자 | 와 열 수를 확인하세요")
        if not all(cells) or any("\x00" in cell for cell in cells): raise DeskError(f"{no}행: 빈 값 및 제어문자 허용 안 함")
        try:
            result.append({key: int(val) if idx else val for idx, (key, val) in enumerate(zip(headers,cells))})
        except ValueError as exc:
            raise DeskError(f"{no}행: 금액과 수량은 정수만 허용됩니다") from exc
    if not result: raise DeskError("한 행 이상 입력하세요")
    return result


class WorknovaGUI:
    def __init__(self, desk: Desk):
        self.desk = desk
        self.root = tk.Tk()
        self.root.title("WORKNOVA Desk — 로컬 계약·납품 장부")
        self.root.geometry("1050x700")
        self.root.minsize(760, 500)
        self.search = tk.StringVar(value="")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        ttk.Label(self.root, text="오프라인·수기 장부입니다. 은행 입금확인·전자서명·세무 신고를 대신하지 않습니다.",
                  font=("Malgun Gothic", 11, "bold")).pack(anchor="w", padx=10, pady=8)
        top=ttk.Frame(self.root); top.pack(fill="x", padx=10)
        ttk.Label(top,text="거래처 검색").pack(side="left")
        ttk.Entry(top,textvariable=self.search, width=35).pack(side="left", padx=6)
        ttk.Button(top,text="새 거래처", command=lambda:self.action(self.new_customer)).pack(side="left", padx=6)
        ttk.Button(top,text="새로고침", command=self.refresh).pack(side="left")
        self.search.trace_add("write",lambda *_:self.refresh())
        tabs=ttk.Notebook(self.root);tabs.pack(fill="both",expand=True,padx=10,pady=8)
        self.views={}
        for label, name, columns in (
          ("거래처","customers",("name","id")),
          ("견적·버전","quotes",("revision","status","total_krw","id")),
          ("계약","contracts",("status","scope","id")),
          ("납품·수금","milestones",("title","status","amount_krw","id"))):
            tab=ttk.Frame(tabs);tabs.add(tab,text=label)
            tree=ttk.Treeview(tab,columns=columns,show="headings",selectmode="browse",height=12)
            for col in columns:
                tree.heading(col,text=col);tree.column(col,width=130 if col!="id" else 270)
            tree.pack(fill="both",expand=True)
            self.views[name]=tree
        self.views["customers"].bind("<<TreeviewSelect>>",lambda _:self.refresh_children("customers"))
        self.views["quotes"].bind("<<TreeviewSelect>>",lambda _:self.refresh_children("quotes"))
        self.views["contracts"].bind("<<TreeviewSelect>>",lambda _:self.refresh_children("contracts"))
        actions=ttk.Frame(self.root);actions.pack(fill="x",padx=10,pady=5)
        button_rows=[ttk.Frame(actions),ttk.Frame(actions),ttk.Frame(actions)]
        for line in button_rows:line.pack(fill="x",anchor="w")
        for idx,(title, fn) in enumerate((
          ("견적 생성",self.new_quote),("견적 수정버전",self.revise_quote),("견적 승인",self.approve_quote),
          ("계약 생성",self.new_contract),("계약 활성화",self.activate),
          ("납품",self.deliver),("수정 요청",self.revision),("납품 승인",self.accept),
          ("수금 수기 기록",self.collect),("견적 HTML 미리보기",self.preview),
          ("장부 백업",self.backup), ("견적 DOCX",self.quote_docx),
          ("현황 DOCX",self.contract_docx), ("견적 PDF (폰트지정)",self.quote_pdf))):
            ttk.Button(button_rows[idx//6],text=title,command=lambda f=fn:self.action(f)).pack(side="left",padx=2,pady=3)
        self.message=tk.StringVar(value="대상 항목을 선택하세요. 확인 후에만 실제 변경됩니다.")
        ttk.Label(self.root,textvariable=self.message).pack(anchor="w",padx=10,pady=5)
        self.refresh()

    def selected(self,name):
        tree=self.views[name]; ids=tree.selection()
        if not ids:raise DeskError(name+": 먼저 행을 선택하세요")
        return ids[0]

    def question(self,title, prompt,initial=""):
        value=simpledialog.askstring(title,prompt,initialvalue=initial,parent=self.root)
        if value is None: raise DeskError("취소했습니다")
        return value

    def confirmed(self,prompt):
        if not messagebox.askyesno("명시적 승인",prompt,parent=self.root): raise DeskError("사용자가 취소했습니다")

    def action(self,fn):
        try:
            result=fn()
            self.message.set("완료(로컬 기록): "+str(result or fn.__name__))
            self.refresh()
        except (DeskError,ValueError,OSError) as exc:
            self.message.set("작업하지 않았습니다: "+str(exc))
            messagebox.showwarning("검토/실패",str(exc),parent=self.root)

    def _put(self,name,rows,cols):
        tree=self.views[name]
        for key in tree.get_children():tree.delete(key)
        for row in rows:
            tree.insert("", "end", iid=row["id"], values=tuple(str(row.get(col,"")) for col in cols))

    def refresh(self):
        # Preserve the operator's selection across writes; no implicit approval or action.
        selected={name:(tree.selection()[0] if tree.selection() else None)
                  for name,tree in self.views.items()}
        rows=self.desk.list_customers(self.search.get())
        self._put("customers",rows,("name","id"))
        self._put("quotes",[],("revision","status","total_krw","id"))
        self._put("contracts",[],("status","scope","id"))
        self._put("milestones",[],("title","status","amount_krw","id"))
        customers=self.views["customers"]
        if selected["customers"] and customers.exists(selected["customers"]):
            customers.selection_set(selected["customers"])
            self.refresh_children("customers")
            quotes=self.views["quotes"]
            if selected["quotes"] and quotes.exists(selected["quotes"]):
                quotes.selection_set(selected["quotes"])
            contracts=self.views["contracts"]
            if selected["contracts"] and contracts.exists(selected["contracts"]):
                contracts.selection_set(selected["contracts"])
                self.refresh_children("contracts")
                steps=self.views["milestones"]
                if selected["milestones"] and steps.exists(selected["milestones"]):
                    steps.selection_set(selected["milestones"])

    def refresh_children(self, kind):
        try:
            if kind=="customers":
                cust=self.selected("customers")
                self._put("quotes",self.desk.list_quotes(cust),("revision","status","total_krw","id"))
                self._put("contracts",self.desk.list_contracts(cust),("status","scope","id"))
            elif kind=="contracts":
                contract=self.selected("contracts")
                self._put("milestones",self.desk.list_milestones(contract),("title","status","amount_krw","id"))
        except DeskError:pass

    def new_customer(self):return self.desk.add_customer(self.question("거래처","거래처 이름"))
    def quote_items(self):return parse_rows(self.question("견적 품목","한 줄마다: 품목|수량|단가(원)\n예: 디자인|2|150000"),kind="quote")
    def vat(self):return messagebox.askyesno("부가세 확인","견적에 10% 부가세를 가산합니까?\n(세무 적합성은 사용자 판단)",parent=self.root)
    def new_quote(self):return self.desk.new_quote(self.selected("customers"),self.quote_items(),taxable=self.vat())
    def revise_quote(self):return self.desk.revise_quote(self.selected("quotes"),self.quote_items(),taxable=self.vat())
    def approve_quote(self):
        q=self.selected("quotes")
        self.confirmed("견적을 승인하면 해당 버전은 변경되지 않습니다. 실제 합의 여부는 직접 확인했습니까?")
        self.desk.approve_quote(q,self.question("승인자","기록할 승인자 이름",'owner'))
    def new_contract(self):
        quote=self.selected("quotes");scope=self.question("범위","계약 작업 범위")
        steps=parse_rows(self.question("단계","한 줄마다: 단계|총액(원)\n승인 견적 총액과 합계가 같아야 합니다"),kind="milestone")
        return self.desk.new_contract(quote,scope,steps)
    def activate(self):
        c=self.selected("contracts");self.confirmed("계약이 실제로 승인되었음을 확인했습니까?")
        self.desk.activate_contract(c,self.question("승인자","승인자 이름",'owner'))
    def deliver(self):self.desk.deliver(self.selected("milestones"),self.question("담당자","납품자 이름",'owner'),self.question("납품 증거","납품 파일/일시 메모"))
    def revision(self):self.desk.request_revision(self.selected("milestones"),self.question("검토자","검토자 이름",'client'),self.question("수정 요청","수정 사유"))
    def accept(self):
        m=self.selected("milestones");self.confirmed("상대방의 납품 검수 승인을 실제로 확인했습니까?")
        self.desk.accept(m,self.question("승인자","승인자 이름",'client'))
    def collect(self):
        m=self.selected("milestones")
        amount=int(self.question("수금 수기 기록","금액 (정수 KRW)"))
        reference=self.question("수금 수기 기록","외부에서 확인한 거래 참조(비밀/계좌번호 입력 금지)")
        self.confirmed("이 기록은 은행에 조회하지 않습니다. 직접 입금 내역을 확인했습니까?")
        return self.desk.record_collection(m,amount,reference,self.question("기록자","기록자",'owner'))
    def preview(self):
        quote=self.selected("quotes")
        file=filedialog.asksaveasfilename(title="새 견적 HTML 저장",defaultextension=".html",filetypes=[("HTML","*.html")],parent=self.root)
        if not file:raise DeskError("저장 취소")
        path=Path(file)
        if path.exists() or path.is_symlink() or not path.parent.is_dir():raise DeskError("기존 파일 덮어쓰기 금지")
        with path.open("x",encoding="utf-8") as f:f.write(self.desk.export_quote_html(quote))
        return "개인정보 없는 새 HTML 미리보기 생성"
    def quote_docx(self):
        return self._export_selected('quote','docx')
    def contract_docx(self):
        return self._export_selected('contract','docx')
    def quote_pdf(self):
        return self._export_selected('quote','pdf')
    def _export_selected(self,kind,format):
        identifier=self.selected('quotes' if kind=='quote' else 'contracts')
        filename=filedialog.asksaveasfilename(title='새 민감정보 제외 문서 저장',defaultextension='.'+format,
                    filetypes=[(format.upper(),'*.{}'.format(format))],parent=self.root)
        if not filename:raise DeskError('문서 저장 취소')
        font=None
        if format=='pdf':
            font=filedialog.askopenfilename(title='상업적으로 사용 가능한 한글 TTF를 본인이 지정하세요',
                                 filetypes=[('TrueType font','*.ttf')],parent=self.root)
            if not font:raise DeskError('한글 PDF 폰트 선택 취소')
        return export_document(self.desk,kind,identifier,filename,format=format,pdf_font=font)

    def backup(self):
        file=filedialog.asksaveasfilename(title="새 SQLite 백업(새 이름)",defaultextension=".sqlite",parent=self.root)
        if not file:raise DeskError("백업 취소")
        return self.desk.backup(file)
    def close(self):self.desk.close();self.root.destroy()
    def run(self):self.root.mainloop()


def main(argv=None):
    parser=argparse.ArgumentParser(description="Offline customer desk GUI")
    parser.add_argument("--db",required=True)
    args=parser.parse_args(argv)
    desk=Desk(args.db)
    if desk.schema_version!=2:
        desk.close()
        raise SystemExit("기존 v1 DB는 CLI migrate-v1 --backup-out 새백업.sqlite를 먼저 실행하세요")
    WorknovaGUI(desk).run()

if __name__=="__main__":main()
