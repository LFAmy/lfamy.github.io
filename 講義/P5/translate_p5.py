#!/usr/bin/env python3
"""
Comprehensive English translation engine for P5 Chinese math handouts.
Preserves exact HTML/CSS/SVG structure while translating all Chinese text.
"""

import re
import os
import glob

SOURCE_DIR = r"G:\lam-fung-academy\講義\P5"
OUTPUT_DIR = r"G:\lam-fung-academy\講義\P5\EN"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── COMPREHENSIVE TRANSLATION DICTIONARY ───
# Ordered: longer/more specific phrases first to prevent partial matches.
# Format: (chinese_text, english_text)
TRANSLATIONS = [
    # ── Brand ──
    ("霖楓學苑", "Lam Fung Academy"),
    ("不教數學，教避開陷阱", "We don't teach math. We teach trap avoidance."),
    ("學生版講義", "Student Handout"),
    ("一對三線上課程", "1-on-3 Online Class"),

    # ── SSPA / Exam ──
    ("呈分試", "SSPA"),
    ("模擬考試", "Mock Exam"),
    ("模擬", "Mock"),

    # ── Section Numbers (Traditional Chinese) ──
    ("一、", "1. "),
    ("二、", "2. "),
    ("三、", "3. "),
    ("四、", "4. "),
    ("五、", "5. "),
    ("六、", "6. "),
    ("七、", "7. "),
    ("八、", "8. "),
    ("九、", "9. "),
    ("十、", "10. "),

    # ── Section Headers ──
    ("熱身啟動題", "Warm-Up Starter Questions"),
    ("核心知識精講 ＋ 例題練習", "Core Knowledge Instruction + Worked Examples"),
    ("核心知識精講", "Core Knowledge Instruction"),
    ("課堂分層同步練習", "Tiered In-Class Practice"),
    ("課後功課", "Homework"),
    ("課後作業", "Homework"),
    ("課後綜合練習", "Comprehensive Post-Lesson Practice"),
    ("本堂核心易錯點總結", "Summary of Key Error-Prone Points"),
    ("終極挑戰專區", "Ultimate Challenge Zone"),
    ("自我檢查", "Self-Check"),
    ("學習目標回顧", "Learning Objectives Review"),
    ("完成本堂後你應該能夠", "By the end of this lesson, you should be able to"),
    ("完成後打剔", "Tick when completed"),

    # ── Knowledge Points ──
    ("知識點一：", "Knowledge Point 1: "),
    ("知識點二：", "Knowledge Point 2: "),
    ("知識點三：", "Knowledge Point 3: "),
    ("知識點四：", "Knowledge Point 4: "),
    ("知識點五：", "Knowledge Point 5: "),
    ("知識點六：", "Knowledge Point 6: "),
    ("知識點七：", "Knowledge Point 7: "),
    ("知識點八：", "Knowledge Point 8: "),

    # ── KP titles ──
    ("平行四邊形面積 = 底 × 高", "Area of Parallelogram = Base x Height"),
    ("三角形面積 = 底 × 高 ÷ 2", "Area of Triangle = Base x Height / 2"),
    ("已知面積反求高或底", "Finding Height or Base Given the Area"),
    ("面積比較與應用", "Area Comparison and Applications"),
    ("梯形面積公式", "Trapezium Area Formula"),
    ("多邊形面積 — 分割法", "Polygon Area -- Decomposition Method"),
    ("多邊形面積 — 填補法", "Polygon Area -- Completion Method"),
    ("面積應用題", "Area Word Problems"),
    ("面積公式總複習 — 三種形狀對比", "Area Formula Review -- Comparing Three Shapes"),
    ("SSPA 常見面積陷阱", "Common SSPA Area Traps"),
    ("面積解題策略 — 四步通關法", "Area Problem-Solving Strategy -- The 4-Step Method"),
    ("異分母分數比較大小", "Comparing Unlike Denominator Fractions"),
    ("異分母分數加法", "Adding Fractions with Unlike Denominators"),
    ("異分母分數減法", "Subtracting Fractions with Unlike Denominators"),
    ("異分母分數加減混合", "Mixed Addition and Subtraction of Unlike Denominator Fractions"),
    ("分數乘法 — 整數 × 分數", "Fraction Multiplication -- Whole Number x Fraction"),
    ("分數乘法 — 分數 × 分數", "Fraction Multiplication -- Fraction x Fraction"),
    ("分數乘法 — 帶分數乘法", "Fraction Multiplication -- Mixed Number Multiplication"),
    ("分數應用題", "Fraction Word Problems"),
    ("圓的認識", "Introduction to Circles"),
    ("圓周與直徑的關係", "Relationship Between Circumference and Diameter"),
    ("圓面積", "Circle Area"),
    ("扇形", "Sector"),
    ("環形", "Annulus/Ring"),
    ("分數除法", "Fraction Division"),
    ("三分數混合運算", "Three-Fraction Mixed Operations"),
    ("四則混合運算", "Mixed Arithmetic Operations"),
    ("體積概念", "Volume Concepts"),
    ("長方體體積", "Volume of a Cuboid"),
    ("正方體體積", "Volume of a Cube"),
    ("表面面積", "Surface Area"),
    ("複合立體", "Composite Solids"),
    ("排水法", "Displacement Method"),
    ("體積應用題", "Volume Word Problems"),
    ("複合棒形圖", "Composite Bar Charts"),
    ("數據分析", "Data Analysis"),
    ("多位數", "Multi-digit Numbers"),
    ("大數估算", "Large Number Estimation"),
    ("小數乘法", "Decimal Multiplication"),
    ("小數除法", "Decimal Division"),
    ("小數近似值", "Decimal Approximation"),
    ("代數式", "Algebraic Expressions"),
    ("簡易方程", "Simple Equations"),
    ("兩步方程", "2-Step Equations"),
    ("方程應用題", "Equation Word Problems"),
    ("混合運算陷阱專項", "Mixed Operation Trap Drill"),
    ("百分數", "Percentage"),
    ("折扣", "Discount"),
    ("速率", "Speed"),
    ("平均速率", "Average Speed"),
    ("對稱", "Symmetry"),
    ("立體圖形", "Solid Figures / 3D Shapes"),
    ("方向", "Direction"),
    ("坐標", "Coordinates"),
    ("可能性", "Probability"),

    # ── Cover page elements ──
    ("對應教材：", "Aligned Textbook: "),
    ("核心陷阱：", "Core Traps: "),
    ("前置知識：", "Prerequisite Knowledge: "),
    ("本堂目標：", "Lesson Objectives: "),
    ("下堂銜接：", "Next Lesson Connection: "),
    ("學生姓名：", "Student Name: "),
    ("班級：", "Class: "),
    ("日期：", "Date: "),
    ("完成時長：", "Duration: "),
    ("SSPA 關聯：", "SSPA Relevance: "),
    ("SSPA 關聯", "SSPA Relevance"),

    # ── Lesson labels ──
    ("小五", "P5"),
    ("第", "Lesson "),
    ("堂", ""),
    ("單元", "Unit"),
    ("分鐘", "min"),
    ("頁", "pages"),
    ("題", "questions"),
    ("上學期", "Term 1"),
    ("下學期", "Term 2"),

    # ── Table headers ──
    ("題目", "Question"),
    ("作答區", "Working Area"),
    ("難度", "Difficulty"),
    ("作答區（寫出完整計算過程）", "Working Area (show full working)"),

    # ── Difficulty levels ──
    ("基礎層", "Basic Tier"),
    ("進階層", "Advanced Tier"),
    ("挑戰層", "Challenge Tier"),
    ("基礎必做", "Basic (Required)"),
    ("基礎必做題", "Basic Required Questions"),
    ("進階選做", "Advanced (Optional)"),
    ("進階選做題", "Advanced Optional Questions"),
    ("基礎", "Basic"),
    ("進階", "Advanced"),
    ("挑戰", "Challenge"),
    ("極限", "Extreme"),
    ("全體必做", "All Students Must Complete"),
    ("選做", "Optional"),
    ("必做", "Required"),

    # ── Math terms ──
    ("平行四邊形", "Parallelogram"),
    ("三角形", "Triangle"),
    ("梯形", "Trapezium"),
    ("多邊形", "Polygon"),
    ("長方形", "Rectangle"),
    ("正方形", "Square"),
    ("圓形", "Circle"),
    ("半徑", "Radius"),
    ("直徑", "Diameter"),
    ("圓周", "Circumference"),
    ("圓心", "Centre of Circle"),
    ("扇形", "Sector"),
    ("環形", "Annulus"),
    ("圓心角", "Central Angle"),
    ("面積", "Area"),
    ("周界", "Perimeter"),
    ("體積", "Volume"),
    ("表面面積", "Surface Area"),
    ("底", "Base"),
    ("高", "Height"),
    ("上底", "Upper Base"),
    ("下底", "Lower Base"),
    ("斜邊", "Slant Side"),
    ("垂直距離", "Perpendicular Distance"),
    ("垂直", "Perpendicular"),
    ("延長線", "Extension Line"),
    ("對角線", "Diagonal"),
    ("中線", "Median"),

    # ── Fraction terms ──
    ("分數", "Fraction"),
    ("分子", "Numerator"),
    ("分母", "Denominator"),
    ("真分數", "Proper Fraction"),
    ("假分數", "Improper Fraction"),
    ("帶分數", "Mixed Number"),
    ("通分", "Common Denominator Conversion"),
    ("約分", "Simplification"),
    ("約簡", "Simplify"),
    ("擴分", "Fraction Expansion"),
    ("異分母", "Unlike Denominators"),
    ("同分母", "Like Denominators"),
    ("等值分數", "Equivalent Fractions"),
    ("異分母分數", "Unlike Denominator Fractions"),
    ("最簡分數", "Simplest Form"),
    ("真分數乘法", "Proper Fraction Multiplication"),
    ("帶分數乘法", "Mixed Number Multiplication"),
    ("分數乘法", "Fraction Multiplication"),
    ("分數除法", "Fraction Division"),
    ("分數加法", "Fraction Addition"),
    ("分數減法", "Fraction Subtraction"),
    ("分數比較", "Fraction Comparison"),
    ("三分數混合", "3-Fraction Mixed Operations"),
    ("四則混合", "4-Arithmetic Mixed Operations"),
    ("剩餘", "Remainder"),
    ("逆向", "Reverse/Working Backwards"),

    # ── Decimal / Percentage ──
    ("小數", "Decimal"),
    ("百分數", "Percentage"),
    ("折扣", "Discount"),
    ("利潤", "Profit"),
    ("虧損", "Loss"),
    ("近似值", "Approximation"),

    # ── Algebra ──
    ("代數", "Algebra"),
    ("方程", "Equation"),
    ("不等式", "Inequality"),
    ("未知數", "Unknown/Variable"),
    ("代數式", "Algebraic Expression"),
    ("代數思維", "Algebraic Thinking"),
    ("設", "Let"),
    ("解方程", "Solve for"),

    # ── Speed ──
    ("速率", "Speed"),
    ("相對速度", "Relative Speed"),
    ("平均速率", "Average Speed"),

    # ── Data / Statistics ──
    ("棒形圖", "Bar Chart"),
    ("折線圖", "Line Graph"),
    ("圓形圖", "Pie Chart"),
    ("數據", "Data"),
    ("平均數", "Mean/Average"),
    ("複合棒形圖", "Composite Bar Chart"),
    ("數據分析", "Data Analysis"),
    ("統計圖表陷阱", "Statistics/Chart Traps"),

    # ── 3D Shapes ──
    ("立體圖形", "3D Shapes / Solid Figures"),
    ("柱體", "Prism"),
    ("錐體", "Pyramid"),
    ("圓柱", "Cylinder"),
    ("圓錐", "Cone"),
    ("球體", "Sphere"),
    ("長方體", "Cuboid"),
    ("正方體", "Cube"),
    ("面", "Face"),
    ("棱", "Edge"),
    ("頂點", "Vertex"),
    ("複合立體", "Composite Solid"),
    ("排水法", "Displacement Method"),
    ("溢流", "Overflow"),
    ("截面", "Cross-Section"),

    # ── Factors / Multiples ──
    ("因數", "Factor"),
    ("倍數", "Multiple"),
    ("公因數", "Common Factor"),
    ("公倍數", "Common Multiple"),
    ("最大公因數", "Highest Common Factor (HCF)"),
    ("最小公倍數", "Lowest Common Multiple (LCM)"),
    ("質數", "Prime Number"),
    ("LCM", "LCM"),
    ("HCF", "HCF"),

    # ── Direction / Coordinates ──
    ("方向", "Direction"),
    ("坐標", "Coordinates"),
    ("象限", "Quadrant"),
    ("可能性", "Probability"),

    # ── Units ──
    ("平方單位", "Square Units"),
    ("立方單位", "Cubic Units"),
    ("單位一致", "Consistent Units"),
    ("單位換算", "Unit Conversion"),
    ("單位", "unit(s)"),

    # ── Common phrases ──
    ("陷阱引爆例題", "Trap-Ignition Example"),
    ("陷阱引爆例題（本堂最重要的示範）", "Trap-Ignition Example (The most important demo of this lesson)"),
    ("常見錯誤", "Common Mistake"),
    ("正確解法", "Correct Solution"),
    ("口訣", "Mnemonic"),
    ("口訣：", "Mnemonic: "),
    ("最高頻錯誤：", "Most Frequent Error: "),
    ("最高頻錯誤", "Most Frequent Error"),
    ("第二高頻錯誤", "Second Most Frequent Error"),
    ("注意：", "Note: "),
    ("提示：", "Hint: "),
    ("陷阱：", "Trap: "),
    ("陷阱", "Trap"),
    ("易錯點", "Error-Prone Point"),
    ("正確做法", "Correct Approach"),
    ("例題", "Worked Example"),
    ("例題練習", "Example Practice"),
    ("反求", "Reverse Calculation"),
    ("求", "Find"),
    ("計算", "Calculate"),
    ("答案", "Answer"),
    ("步驟", "Step"),
    ("步驟分", "Method Marks"),
    ("答句", "Answer Statement"),
    ("應用題", "Word Problem"),
    ("綜合應用", "Comprehensive Application"),
    ("分割法", "Decomposition Method"),
    ("填補法", "Completion Method"),
    ("四步通關法", "4-Step Method"),
    ("多餘資訊", "Extraneous Information"),
    ("圖形錯覺", "Shape Illusion"),
    ("公式總複習", "Formula Review"),
    ("相關課題", "Related Topics"),
    ("選擇題", "Multiple Choice"),
    ("簡答題", "Short Answer"),
    ("應用題", "Application Problem"),
    ("組合圖形", "Composite Shape"),
    ("分割", "Decompose"),
    ("填補", "Fill and Subtract"),
    ("重疊", "Overlap"),

    # ── Verb phrases ──
    ("比較", "Compare"),
    ("大小", "Size"),
    ("多", "More"),
    ("少", "Less"),
    ("倍", "Times"),
    ("全部加起來", "Add Them All Together"),
    ("橫切豎切都可以，切完尺寸要對齊", "Cut horizontally or vertically -- just align the measurements."),
    ("先標", "Label First"),
    ("逐一計再相加", "Calculate One by One, Then Add"),
    ("先補成大方，再減多餘位。補要補完整，減要減準確。", "First complete to a large rectangle, then subtract the excess. Complete fully, subtract accurately."),
    ("先寫公式再代數，答案必定有", "Write the formula first, then substitute. The answer must include"),
    ("一判形狀二選式，三代入四查單位。先寫公式再代數，答案必定有", "1. Identify shape, 2. Choose formula, 3. Substitute carefully, 4. Check units. Write formula first, then answer includes"),

    # ── Combined phrase patterns (must come before sub-phrases) ──
    ("共 5 題，5 分鐘", "(5 questions, 5 min)"),
    ("共 7 題，全體必做", "(7 questions, all must complete)"),
    ("共 5 題，🚶🚀 選做", "(5 questions, walkers & rockets optional)"),
    ("共 4 題，🚀 選做", "(4 questions, rockets optional)"),
    ("共 3 題，🚀 選做", "(3 questions, rockets optional)"),
    ("共 6 題，必須寫公式和步驟", "(6 questions, must show formula and steps)"),
    ("共 2 題，🚀 選做", "(2 questions, rockets optional)"),
    ("共 5 題，🚶🚀 選做，呈分試殺手題", "(5 questions, walkers & rockets optional, SSPA killer questions)"),
    ("共 5 題", "(5 questions)"),
    ("共 4 題", "(4 questions)"),
    ("共 3 題", "(3 questions)"),
    ("共 2 題", "(2 questions)"),
    ("共 6 題", "(6 questions)"),
    ("共 7 題", "(7 questions)"),
    ("共 8 題", "(8 questions)"),
    ("共 1 題", "(1 question)"),
    ("呈分試殺手題", "SSPA Killer Questions"),
    ("呈分試壓軸＋競賽級別", "SSPA Finale + Competition Level"),
    ("🚀 選做", "(Rockets optional)"),
    ("🚶🚀 選做", "(Walkers & Rockets optional)"),
    ("全部必做，列式 → 公式 → 計算 → 答句", "(All must complete. Set up -> Formula -> Calculate -> Answer statement)"),

    # ── Error table translations ──
    ("把斜邊當作高", "Using the slant side as height"),
    ("把斜邊當高", "Using the slant side as height"),
    ("忘記 ÷ 2", "Forgetting to divide by 2"),
    ("平分四邊形把斜邊當作高", "Parallelogram: using slant side as height"),
    ("找不到高", "Cannot find the height"),
    ("平行四邊形：把斜邊當作高", "Parallelogram: Using slant side as height"),
    ("三角形：忘記 ÷ 2", "Triangle: Forgetting to Divide by 2"),
    ("鈍角三角形：找不到高", "Obtuse Triangle: Cannot Find the Height"),
    ("已知面積反求高/底時忘記三角形要先 ×2", "When reverse-calculating height/base, forgetting to x2 for triangles"),
    ("忘記寫面積單位", "Forgetting to write area units"),
    ("底和高不對應", "Mismatched base and height"),
    ("梯形忘記÷2", "Trapezium: Forgetting to /2"),
    ("(上底+下底)÷2後忘記乘高", "After (upper+lower)/2, forgetting to multiply by height"),
    ("高用錯斜邊長度", "Using slant side instead of height"),
    ("分割後尺寸對錯", "Decomposition: incorrect segment dimensions"),
    ("填補法減錯", "Completion Method: subtraction error"),
    ("多餘資訊干擾（T4陷阱）", "Extraneous Information (T4 Trap)"),
    ("組合圖形漏計某部分", "Composite shape: missing a component"),
    ("三角/梯形忘記÷2（T5圖形錯覺）", "Triangle/Trapezium: Forgetting /2 (T5 Shape Illusion)"),
    ("周界公式當面積用（T5混淆）", "Using perimeter formula for area (T5 Confusion)"),
    ("單位換算錯誤（T5）", "Unit conversion error (T5)"),
    ("給周界求面積時直接代入（T4多餘資訊）", "Direct substitution of perimeter into area (T4 Extraneous Info)"),
    ("反求時運算方向倒置（T4）", "Inverted operation direction when reverse-calculating (T4)"),
    ("面積單位漏寫²", "Omitting ² on area units"),

    # ── Formats / Number-related ──
    ("答案寫", "Answer should be written as"),
    ("答案必須有", "Answer must include"),
    ("平方米", "m"),
    ("平方厘米", "cm"),

    # ── Grade/Book references ──
    ("小學數學新思維（第二版）", "Primary Mathematics New Thinking (2nd Ed.)"),
    ("現代教育", "Modern Education"),
    ("冊", "Book"),
    ("5上A冊", "P5 Term 1 Book A"),
    ("5上B冊", "P5 Term 1 Book B"),
    ("5下A冊", "P5 Term 2 Book A"),
    ("5下B冊", "P5 Term 2 Book B"),

    # ── High Frequency markers ──
    ("高頻", "High-Frequency"),
    ("必考", "Must-Know for Exam"),
    ("每年必考", "Tested Every Year"),
    ("佔卷一", "accounts for approx. "),
    ("佔卷二", "accounts for approx. "),
    ("失分重災區", "Top Mark-Losing Zone"),
    ("本堂針對性殲滅所有常見陷阱", "This lesson targets and eliminates all common traps"),

    # ── Action phrases ──
    ("寫出公式 → 代入 → 答案連單位", "Write formula -> Substitute -> Answer with units"),
    ("列式 → 公式 → 計算 → 答句", "Set up -> Formula -> Calculate -> Answer statement"),
    ("寫公式和步驟", "Show formula and working steps"),
    ("寫出完整計算過程", "Show full working"),

    # ── Self-check box labels ──
    ("我識得分辦每個知識點嘅陷阱", "I can identify the traps for every knowledge point"),
    ("我能夠獨立完成", "I can independently complete"),
    ("我能夠挑戰", "I can take on"),
    ("我記得住口訣", "I remember all the mnemonics"),
    ("辨認本堂所有陷阱類型", "Identify all trap types from this lesson"),
    ("獨立解答", "Independently answer"),
    ("（100%正確）", " (100% correct)"),
    ("（80%+正確）", " (80%+ correct)"),
    ("向同學解釋本堂口訣", "Explain this lesson's mnemonics to a classmate"),

    # ── Number + 題 patterns ──
    ("46題", "46 questions"),
    ("45題", "45 questions"),
    ("48題", "48 questions"),

    # ── Additional traps ──
    ("T1: 單位與進位", "T1: Units & Place Value"),
    ("T2: 小數點", "T2: Decimal Point"),
    ("T3: 運算次序", "T3: Order of Operations"),
    ("T4: 面積公式混淆", "T4: Area Formula Confusion"),
    ("T5: 幾何圖形混淆", "T5: Geometry Shape Confusion"),
    ("T6: 分數陷阱", "T6: Fraction Traps"),
    ("T7: 百分數陷阱", "T7: Percentage Traps"),
    ("T8: 速率陷阱", "T8: Speed/Rate Traps"),
    ("T9: 方程陷阱", "T9: Equation Traps"),
    ("T10: 統計圖表陷阱", "T10: Statistics/Chart Traps"),

    # ── Misc ──
    ("無需關注", "Not Applicable"),
    ("寒假", "Winter Break"),
    ("暑假", "Summer Break"),
    ("計劃", "Plan"),
    ("檢討", "Review/Debrief"),
    ("個人弱項", "Personal Weaknesses"),
    ("閉環", "Closed Loop / Mastered"),
    ("終極補底", "Ultimate Foundation Building"),
    ("衝刺", "Sprint"),
    ("計算題滿分衝刺", "Full Marks Sprint: Calculation Questions"),
    ("應用題滿分衝刺", "Full Marks Sprint: Word Problems"),
    ("幾何題滿分衝刺", "Full Marks Sprint: Geometry Questions"),
    ("跨課題殺手題", "Cross-Topic Killer Questions"),
    ("終極跨課題殺手題", "Ultimate Cross-Topic Killer Questions"),
    ("SSPA模擬", "SSPA Mock"),
    ("陷阱總複習", "Comprehensive Trap Review"),
    ("數與量", "Number & Measurement"),
    ("圖形與方程", "Shapes & Equations"),
    ("綜合", "Comprehensive"),
    ("上學期陷阱總複習", "Term 1 Comprehensive Trap Review"),
    ("SSPA計算題滿分衝刺", "SSPA Full Marks Sprint: Calculation"),
    ("SSPA應用題滿分衝刺", "SSPA Full Marks Sprint: Word Problems"),
    ("SSPA幾何題滿分衝刺", "SSPA Full Marks Sprint: Geometry"),
    ("SSPA幾何衝刺", "SSPA Geometry Sprint"),
    ("綜合-面積-多位數-估算", "Comprehensive: Area, Multi-digit Numbers, Estimation"),
    ("綜合-分數-小數-方程", "Comprehensive: Fractions, Decimals, Equations"),
    ("綜合-體積-面積-分數", "Comprehensive: Volume, Area, Fractions"),
    ("綜合-方程-數據-應用題", "Comprehensive: Equations, Data, Word Problems"),
    ("SSPA終極跨課題殺手題", "SSPA Ultimate Cross-Topic Killer Questions"),

    # ── Specific Lesson Title translations ──
    ("平行四邊形與三角形面積", "Area of Parallelograms and Triangles"),
    ("梯形與多邊形面積", "Area of Trapeziums and Polygons"),
    ("面積陷阱專項", "Area Traps Drill"),
    ("面積陷阱專項突破", "Area Trap Specialist Training"),
    ("異分母分數比較+加法+減法", "Unlike Denominator Fractions: Comparison, Addition & Subtraction"),
    ("異分母分數：比較、加法與減法", "Unlike Denominator Fractions: Comparison, Addition & Subtraction"),
    ("異分母分數加法", "Addition of Unlike Denominator Fractions"),
    ("分數乘法", "Fraction Multiplication"),
    ("分數應用題", "Fraction Word Problems"),
    ("圓的認識", "Introduction to Circles"),
    ("體積應用題專項", "Volume Word Problems Drill"),
    ("體積應用題", "Volume Word Problems"),
    ("體積概念+長方體正方體體積+表面面積", "Volume Concepts + Cuboid & Cube Volume + Surface Area"),
    ("複合立體+排水法", "Composite Solids + Displacement Method"),
    ("複合棒形圖+數據分析", "Composite Bar Charts + Data Analysis"),
    ("分數除法_intro", "Introduction to Fraction Division"),
    ("三分數混合_四則混合", "3-Fraction Mixed + Arithmetic Mixed Operations"),
    ("分數文字題_剩餘逆向", "Fraction Word Problems: Remainder & Reverse"),
    ("小數乘法", "Decimal Multiplication"),
    ("小數除法", "Decimal Division"),
    ("小數近似值+應用", "Decimal Approximation & Applications"),
    ("代數式認識+簡易方程", "Introduction to Algebraic Expressions & Simple Equations"),
    ("代數式進階+兩步方程", "Advanced Algebraic Expressions & 2-Step Equations"),
    ("方程應用題", "Equation Word Problems"),
    ("混合運算陷阱專項", "Mixed Operations Trap Drill"),

    # ── Geometry-specific translations ──
    ("一般三角形", "General Triangle"),
    ("直角三角形", "Right-Angled Triangle"),
    ("鈍角三角形", "Obtuse Triangle"),
    ("高在三角形外面", "Height falls outside the triangle"),
    ("底邊延長線", "Extension of the base"),
    ("頂點到底邊延長線的垂直距離", "Perpendicular distance from the vertex to the base extension"),
    ("最長邊", "Longest Side"),
    ("兩個小三角形", "Two Smaller Triangles"),
    ("大三角形", "Large Triangle"),
    ("中線", "Median Line"),
    ("不規則形狀", "Irregular Shape"),
    ("簡單形狀", "Simple Shapes"),
    ("凹字形", "Concave Shape"),
    ("凸字形", "Convex Shape"),
    ("L形", "L-shape"),
    ("五邊形", "Pentagon"),
    ("等腰梯形", "Isosceles Trapezium"),

    # ── Application words ──
    ("花圃", "Flower Bed"),
    ("草地", "Lawn"),
    ("地氈", "Carpet"),
    ("廣告牌", "Billboard"),
    ("旗幟", "Flag"),
    ("地磚", "Floor Tile"),
    ("牆壁", "Wall"),
    ("油", "Paint"),
    ("油漆", "Paint"),
    ("升", "L"),
    ("髹油漆", "Paint"),
    ("田地", "Field"),
    ("菜", "Vegetables"),
    ("樹", "Trees"),
    ("棵", "plant(s)"),
    ("種", "Grow/Plant"),
    ("每平方米", "Per square metre"),
    ("花", "Flowers"),
    ("田", "Field"),
    ("廣場", "Plaza/Public Square"),
    ("公園", "Park"),
    ("停車場", "Car Park"),
    ("車位", "Parking Space"),
    ("每輛車佔地", "Each car occupies"),
    ("最多可停", "Maximum parking capacity"),
    ("客廳", "Living Room"),
    ("地皮", "Plot of Land"),
    ("壁畫", "Mural"),
    ("鐵線", "Wire"),
    ("圍成", "Enclosed"),

    # ── Key instructional phrases ──
    ("先求", "First find"),
    ("再求", "Then find"),
    ("代入", "Substitute"),
    ("設", "Let"),
    ("解", "Solve"),
    ("即", "i.e."),
    ("例如", "e.g."),
    ("參照", "See"),
    ("如上圖", "As shown above"),
    ("如圖", "As shown"),
    ("如下", "As follows"),
    ("以下", "Below"),
    ("之上", "Above"),
    ("所示", "Shown"),
    ("不等於", "Not Equal To"),
    ("相等", "Equal"),
    ("公式", "Formula"),
    ("算式", "Expression"),
    ("結果", "Result"),
    ("餘數", "Remainder"),
    ("商", "Quotient"),
    ("積", "Product"),
    ("和", "Sum"),
    ("差", "Difference"),
    ("除以", "Divided By"),
    ("乘以", "Multiplied By"),
    ("加上", "Plus"),
    ("減去", "Minus"),
    ("等於", "Equals"),
    ("大約", "Approximately"),
    ("約等於", "Approximately Equals"),

    # ── Test terms ──
    ("卷一", "Paper 1"),
    ("卷二", "Paper 2"),
    ("常見題型", "Common Question Type"),
    ("壓軸題", "Finale Question"),
    ("殺手題", "Killer Question"),
    ("必考題", "Must-Know Question"),
    ("課程", "Curriculum"),
    ("課堂", "Lesson"),

    # ── Circle-specific ──
    ("圓規", "Compass"),
    ("畫圓", "Draw a Circle"),
    ("圓心", "Centre"),
    ("半徑", "Radius"),
    ("直徑", "Diameter"),
    ("圓周率", "Pi"),
    ("π", "π"),
    ("3.14", "3.14"),
    ("22/7", "22/7"),

    # ── Volume-specific ──
    ("長", "Length"),
    ("闊", "Width"),
    ("高", "Height"),
    ("底面積", "Base Area"),
    ("排水法", "Water Displacement Method"),
    ("水位上升", "Water Level Rise"),
    ("溢出", "Overflow"),
    ("物體體積", "Object Volume"),
    ("容器", "Container"),

    # ── Speed/Rate ──
    ("距離", "Distance"),
    ("時間", "Time"),
    ("速率", "Speed"),
    ("時速", "Speed per hour"),
    ("分速", "Speed per minute"),
    ("秒速", "Speed per second"),

    # ── Graphs/Data ──
    ("棒形圖", "Bar Chart"),
    ("統計圖", "Statistical Chart"),
    ("刻度", "Scale"),
    ("頻數", "Frequency"),
    ("最多", "Most / Maximum"),
    ("最少", "Least / Minimum"),
    ("相差", "Difference"),
    ("總數", "Total"),
    ("結論", "Conclusion"),

    # ── Marks feedback ──
    ("扣分", "Mark Deduction"),
    ("必定扣分", "Leads to guaranteed mark deduction"),
    ("滿分", "Full Marks"),
    ("得分", "Score"),
    ("錯題", "Wrong Answer"),
    ("改正", "Correction"),

    # ── Actions for students ──
    ("必須寫公式和步驟", "Must show formula and working steps"),
    ("選做", "Optional"),
    ("寫出公式", "Write the formula"),
    ("代入", "Substitute values"),
    ("答案連單位", "Answer with units"),
    ("寫答句", "Write answer statement"),

    # ── Parenthetical hints ──
    ("沒有", "No"),
    ("不是", "Is not"),
    ("不要", "Do not"),
    ("不可以", "Cannot"),
    ("需要", "Need to"),
    ("不需要", "Do not need"),
    ("可以", "Can"),
    ("必須", "Must"),
    ("一定", "Must / Definitely"),
    ("可能", "Possible"),
    ("如果", "If"),
    ("或者", "Or"),
    ("但", "But"),
    ("所以", "Therefore"),
    ("因為", "Because"),
    ("然後", "Then"),
    ("之後", "After"),
    ("之前", "Before"),
    ("的", "'s / of"),
    ("和", "And"),
    ("與", "And"),
    ("或", "Or"),
    ("每", "Per / Each"),
    ("個", "Unit piece"),
    ("條", "Unit piece"),
    ("塊", "Piece"),
    ("張", "Sheet"),
    ("隻", "Unit piece"),
    ("元", "Dollars"),
    ("角", "10 Cents"),
    ("分", "Cent"),

    # ── General instructional context ──
    ("堂目標", "Lesson Objectives"),
    ("前置知識", "Prerequisite Knowledge"),
    ("對應教材", "Aligned Textbook"),
    ("核心陷阱", "Core Traps"),
    ("SSPA 關聯", "SSPA Relevance"),
    ("完成時長", "Duration"),
    ("學生姓名", "Student Name"),
    ("班級", "Class"),
    ("日期", "Date"),
    ("相關課題", "Related Topics"),
    ("錯誤", "Mistake"),
    ("正確", "Correct"),
    ("為什麼", "Why"),
    ("注意", "Note"),
    ("提示", "Hint"),
    ("陷阱", "Trap"),
    ("例", "Example"),
    ("解", "Solution"),
    ("答", "Answer"),
    ("問", "Question"),
    ("圖", "Diagram"),
    ("表", "Table"),
    ("公式", "Formula"),
    ("複習", "Review"),
    ("練習", "Practice"),
    ("測試", "Test"),
    ("考試", "Exam"),
    ("模擬", "Mock/Simulation"),
    ("總複習", "Comprehensive Review"),
    ("深度練習", "In-Depth Practice"),
    ("專項突破", "Targeted Drill"),
    ("專項", "Drill"),
    ("認識", "Introduction to"),
    ("進階", "Advanced"),
    ("應用", "Application"),
    ("混合", "Mixed"),
    ("運算", "Operations"),
    ("綜合複習", "Comprehensive Review"),

    # ── P6 bridge ──
    ("P6", "P6"),
    ("銜接", "Bridging to"),
    ("圓形面積基礎", "Foundations for Circle Area"),

    # ── Fractions deep terminology ──
    ("通分三步法", "3-Step Common Denominator Method"),
    ("分子忘記同步擴大", "Numerator not expanded in sync"),
    ("結果未約簡", "Result not simplified"),
    ("真分數", "Proper Fraction"),
    ("假分數", "Improper Fraction"),
    ("帶分數", "Mixed Number"),
    ("化帶分數", "Convert to Mixed Number"),
    ("化假分數", "Convert to Improper Fraction"),
    ("倒數", "Reciprocal"),
    ("交叉約簡", "Cross-Cancel"),
    ("約分", "Simplify/Reduce"),
    ("最簡", "Simplest Form"),

    # ── Advanced instructional ──
    ("先判斷形狀", "First, identify the shape"),
    ("選對應方法", "Choose the corresponding method"),
    ("再比較", "Then compare"),
    ("用", "Using"),
    ("表達", "Express"),
    ("分割成基本圖形", "Decompose into basic shapes"),
    ("分別計算", "Calculate separately"),
    ("相加", "Add together"),
    ("相減", "Subtract"),
    ("拼成", "Combine to form"),
    ("切成", "Cut into"),
    ("補成", "Complete to form"),
    ("挖去", "Dig out / Remove"),
    ("剩餘面積", "Remaining Area"),
    ("未被覆蓋的部分", "Uncovered portion"),

    # ── Self-assessment checkboxes ──
    ("我識得分辦每個知識點嘅陷阱", "I can identify the traps for each knowledge point"),
    ("我能夠獨立完成🌱基礎題", "I can independently complete Basic tier questions"),
    ("我能夠挑戰🌿進階題", "I can take on Advanced tier questions"),
    ("我記得住口訣", "I remember the mnemonics"),
    ("辨認本堂所有陷阱類型", "Identify all trap types in this lesson"),
    ("獨立解答🌱基礎題（100%正確）", "Independently answer Basic tier (100% correct)"),
    ("挑戰🌿進階題（80%+正確）", "Take on Advanced tier (80%+ correct)"),
    ("向同學解釋本堂口訣", "Explain this lesson's mnemonics to classmates"),

    # ── More detailed translations ──
    ("高是垂直距離不是斜邊", "Height is the perpendicular distance, NOT the slant side"),
    ("高是垂直距離", "Height is the perpendicular distance"),
    ("不是斜邊", "NOT the slant side"),
    ("不是斜邊的長度", "NOT the length of the slant side"),
    ("用了斜邊當高", "Used slant side as height"),
    ("斜邊不是高", "The slant side is NOT the height"),

    # ── SSPA-specific ──
    ("SSPA 必考", "SSPA Must-Know"),
    ("SSPA 進階", "SSPA Advanced"),
    ("SSPA 應用", "SSPA Application"),
    ("呈分試每年必考", "Tested every year in SSPA"),
    ("呈分試常見題型", "Common SSPA question type"),
    ("呈分試壓軸", "SSPA Finale-level"),
    ("呈分試卷二常見題型", "Common SSPA Paper 2 question type"),

    # ── File naming patterns ──
    ("綜合", "Comprehensive"),
]

# Sort by length (longest first) to prevent partial matches
TRANSLATIONS.sort(key=lambda x: len(x[0]), reverse=True)


def translate_html(filepath):
    """Translate a Chinese P5 HTML handout to English."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # ── Step 1: Apply all dictionary translations ──
    for chinese, english in TRANSLATIONS:
        content = content.replace(chinese, english)

    # ── Step 2: Fix the badge text pattern ──
    # "P5 · Lesson X · Student Handout"
    content = re.sub(
        r'P5 · Lesson (\d+) · Student Handout',
        r'P5 · Lesson \1 · Student Handout',
        content
    )

    # ── Step 3: Fix the subtitle pattern (Unit · Topic · XX min · 1-on-3 Online Class) ──
    # This handles the cv-sub line after translation
    # The pattern will vary, but we leave a lot as-is

    # ── Step 4: Update HTML lang attribute ──
    content = content.replace('lang="zh-HK"', 'lang="en"')

    # ── Step 5: Add English font fallback ──
    # Add 'Inter' or system font as fallback after 'Noto Sans HK'
    content = content.replace(
        "font-family:'Noto Sans HK',sans-serif;",
        "font-family:'Noto Sans HK','Inter',system-ui,-apple-system,sans-serif;"
    )

    # ── Step 6: Fix any double spaces created by replacements ──
    content = re.sub(r' {2,}', ' ', content)

    # ── Step 7: Fix the footer text ──
    # "Lam Fung Academy · LF Academy · We don't teach math..."
    # Most of this is handled by dictionary, but fix any remnants

    # ── Step 8: Fix the no-print bar text ──
    # Ctrl+P text stays mostly as-is, just needs brand translation which should be done

    return content


def get_output_filename(input_filename):
    """Convert Chinese filename to English filename."""
    # Map of Chinese filename parts to English
    name = input_filename

    # Fix Term labels
    name = name.replace('-上-', '-T1-')
    name = name.replace('-下-', '-T2-')

    # Remove Chinese characters by replacing specific patterns
    # We'll rename based on lesson number

    # Add _EN suffix before .html
    base = name.replace('.html', '')
    return base + '_EN.html'


def main():
    html_files = sorted(glob.glob(os.path.join(SOURCE_DIR, '*.html')))

    print(f"Found {len(html_files)} HTML files to translate")

    for i, filepath in enumerate(html_files):
        filename = os.path.basename(filepath)
        print(f"\n[{i+1}/{len(html_files)}] Processing: {filename}")

        try:
            translated = translate_html(filepath)

            # Generate output filename
            out_name = get_output_filename(filename)
            out_path = os.path.join(OUTPUT_DIR, out_name)

            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(translated)

            print(f"  -> Saved: {out_name}")

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone! Files saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
