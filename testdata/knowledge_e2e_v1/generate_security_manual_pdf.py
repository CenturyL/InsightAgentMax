from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "05_澄海智造_AI演示平台安全运行手册_v1.pdf"


def _footer(canvas, document):
    canvas.saveState()
    canvas.setFont("STSong-Light", 9)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(20 * mm, 12 * mm, "CHIM-AI-SEC-006 | 内部测试文档")
    canvas.drawRightString(190 * mm, 12 * mm, f"第 {document.page} 页")
    canvas.restoreState()


def build_pdf() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "BodyCN",
        parent=styles["BodyText"],
        fontName="STSong-Light",
        fontSize=10.5,
        leading=17,
        textColor=colors.HexColor("#243247"),
        spaceAfter=7,
    )
    title = ParagraphStyle(
        "TitleCN",
        parent=body,
        fontSize=23,
        leading=31,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F4C81"),
        spaceAfter=14,
    )
    subtitle = ParagraphStyle(
        "SubtitleCN",
        parent=body,
        fontSize=11,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
    )
    heading = ParagraphStyle(
        "HeadingCN",
        parent=body,
        fontSize=15,
        leading=22,
        textColor=colors.HexColor("#0F4C81"),
        spaceBefore=10,
        spaceAfter=8,
    )
    small = ParagraphStyle("SmallCN", parent=body, fontSize=9, leading=14)

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=22 * mm,
        title="澄海智造集团 AI 演示平台安全运行手册",
        author="澄海智造集团安全与平台工程部",
    )
    story = [
        Spacer(1, 28 * mm),
        Paragraph("澄海智造集团", subtitle),
        Paragraph("AI 演示平台安全运行手册", title),
        Paragraph("文档编号：CHIM-AI-SEC-006", subtitle),
        Paragraph("版本：V1.0 | 生效日期：2026-08-20", subtitle),
        Spacer(1, 16 * mm),
        Table(
            [
                ["适用环境", "求职演示与受控体验环境"],
                ["责任部门", "安全与平台工程部"],
                ["审阅周期", "每 90 天或重大架构变更后"],
                ["关键代号", "星盾模式"],
            ],
            colWidths=[38 * mm, 95 * mm],
            style=TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F1F8")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#243247")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C7D6")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            ),
        ),
        PageBreak(),
        Paragraph("1. 安全目标", heading),
        Paragraph("平台的首要目标是展示 Agent、长期记忆和知识检索能力，同时限制工具权限、模型费用、网络暴露和服务器资源消耗。演示便利性不得覆盖最小权限、可追溯和可停止原则。", body),
        Paragraph("2. 星盾模式", heading),
        Paragraph("当发生异常工具循环、调用费用快速上升、未知外联、跨会话数据混淆或服务器资源持续超过阈值时，值班人员应启用“星盾模式”。星盾模式会停止新的 Agent 请求，保留健康检查和只读会话查询，并关闭可执行代码、文件系统写入和外部 MCP 工具。", body),
        Paragraph("星盾模式触发后，必须先保留请求 trace、模型 usage、检索 usage 和系统指标，再进行进程重启。不得为了快速恢复而清空事实账本。", body),
        Paragraph("3. 工具权限基线", heading),
        Table(
            [
                ["能力", "演示环境策略", "原因"],
                ["知识检索", "允许，只读", "核心展示能力"],
                ["时间查询", "允许", "低风险工具"],
                ["Shell / Python 执行", "默认禁用", "避免主机命令执行"],
                ["文件系统写入", "默认禁用", "避免覆盖项目和密钥"],
                ["前台 MCP 配置", "不提供", "避免访客扩大工具面"],
            ],
            colWidths=[38 * mm, 43 * mm, 75 * mm],
            repeatRows=1,
            style=TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C7D6")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        ),
        Paragraph("4. 调用与费用限制", heading),
        Paragraph("聊天模型采用全局、来源 IP 和单请求三层限制；Embedding 与 Reranker 使用独立额度账本。演示环境建议每日聊天模型费用上限为 1 美元等值，检索模型费用上限为 0.10 美元等值。任何 pending 预留都必须设置过期时间并由启动对账回收。", body),
        Paragraph("同一幂等键的重复请求只能产生一次有效结算；费用达到 80% 时记录预警，达到 100% 时拒绝新调用，不允许绕过线上额度改走未受控模型。", body),
        Paragraph("5. 网络与数据库", heading),
        Paragraph("公网入口只暴露前端和网关需要的端口。后端数据库不得直接暴露到公网；知识库、长期记忆、Session、Trace 和额度事实统一保存在 PostgreSQL。外部模型 API 必须配置连接超时、总超时、有限重试和指数退避。", body),
        Paragraph("数据库备份的演示恢复目标为 RTO 30 分钟、RPO 24 小时。每次结构变更前都应完成逻辑备份并记录 SHA256，且至少进行一次恢复演练。", body),
        Paragraph("6. 事件处置步骤", heading),
        Paragraph("第一步：停止新请求并启用星盾模式。第二步：记录时间、请求标识、客户端来源、模型和工具 trace。第三步：确认是否存在重复扣费、数据越权或主机命令执行。第四步：按 CHIM-OPS-014 的蓝鲸回滚阈值决定回滚。第五步：恢复后完成数据对账和事件复盘。", body),
        Paragraph("7. 验收清单", heading),
        Paragraph("上线前必须确认：公网工具白名单符合预期；同幂等键并发只有一个 winner；每日额度到顶会稳定拒绝；PostgreSQL 重启后 Session 和知识数据仍存在；删除本地临时文件不影响已提交数据；检索结果能够返回来源和引用。", body),
        Spacer(1, 8 * mm),
        Paragraph("本手册中的企业、系统和参数均为专业演示测试数据，不代表真实生产环境。", small),
    ]
    document.build(story, onFirstPage=_footer, onLaterPages=_footer)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
