#!/usr/bin/env python3
import sys

class PDFWriter:
    def __init__(self, page_width=612, page_height=792):
        self.width = page_width
        self.height = page_height
        self.margin_x = 50
        self.margin_top = 50
        self.margin_bottom = 50
        self.usable_width = self.width - 2 * self.margin_x
        
        self.pages = [] # list of stream bytearrays
        self.current_stream = []
        self.y = self.height - self.margin_top
        self.page_number = 1
        
    def _start_page(self):
        self.current_stream = []
        self.y = self.height - self.margin_top
        
    def _end_page(self):
        # Add footer (page number)
        footer = [
            "BT",
            "/F1 9 Tf",
            "0.5 0.5 0.5 rg",
            f"1 0 0 1 {self.width/2 - 20} {self.margin_bottom - 20} Tm",
            f"(Page {self.page_number}) Tj",
            "ET"
        ]
        self.current_stream.extend(footer)
        stream_bytes = "\n".join(self.current_stream).encode('latin1')
        self.pages.append(stream_bytes)
        self.page_number += 1
        
    def check_space(self, needed_height):
        if self.y - needed_height < self.margin_bottom:
            self._end_page()
            self._start_page()

    def add_title(self, title, subtitle):
        self.check_space(70)
        # Decorative bar
        self.current_stream.append("0.12 0.44 0.76 rg")
        self.current_stream.append(f"{self.margin_x} {self.y - 4} {self.usable_width} 3 re f")
        
        # Main Title
        self.current_stream.append("BT")
        self.current_stream.append("/F2 20 Tf")
        self.current_stream.append("0.08 0.18 0.32 rg")
        self.current_stream.append(f"1 0 0 1 {self.margin_x} {self.y} Tm")
        clean_title = title.replace("(", "\\(").replace(")", "\\)")
        self.current_stream.append(f"({clean_title}) Tj")
        self.current_stream.append("ET")
        self.y -= 22
        
        # Subtitle
        self.current_stream.append("BT")
        self.current_stream.append("/F1 11 Tf")
        self.current_stream.append("0.4 0.45 0.5 rg")
        self.current_stream.append(f"1 0 0 1 {self.margin_x} {self.y} Tm")
        clean_sub = subtitle.replace("(", "\\(").replace(")", "\\)")
        self.current_stream.append(f"({clean_sub}) Tj")
        self.current_stream.append("ET")
        self.y -= 28

    def add_section_header(self, text):
        self.check_space(45)
        self.y -= 10
        self.current_stream.append("BT")
        self.current_stream.append("/F2 13 Tf")
        self.current_stream.append("0.1 0.25 0.45 rg")
        self.current_stream.append(f"1 0 0 1 {self.margin_x} {self.y} Tm")
        clean_text = text.replace("(", "\\(").replace(")", "\\)")
        self.current_stream.append(f"({clean_text}) Tj")
        self.current_stream.append("ET")
        self.y -= 4
        # subtle underline
        self.current_stream.append("0.85 0.88 0.92 RG 1 w")
        self.current_stream.append(f"{self.margin_x} {self.y} m {self.margin_x + self.usable_width} {self.y} l S")
        self.y -= 16

    def add_paragraph(self, text, bold_prefix=""):
        # Wrap words
        words = text.split(" ")
        lines = []
        cur_line = []
        # approximate char limit per line for 10pt font in 512pt width ~ 85-90 chars
        max_chars = 82
        
        prefix_len = len(bold_prefix)
        char_count = prefix_len
        
        for w in words:
            if char_count + len(w) + 1 > max_chars:
                lines.append(" ".join(cur_line))
                cur_line = [w]
                char_count = len(w)
            else:
                cur_line.append(w)
                char_count += len(w) + 1
        if cur_line:
            lines.append(" ".join(cur_line))
            
        needed = len(lines) * 14 + 6
        self.check_space(needed)
        
        for i, line in enumerate(lines):
            self.current_stream.append("BT")
            line_escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if i == 0 and bold_prefix:
                bp_escaped = bold_prefix.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                self.current_stream.append("/F2 10 Tf")
                self.current_stream.append("0.15 0.15 0.15 rg")
                self.current_stream.append(f"1 0 0 1 {self.margin_x} {self.y} Tm")
                self.current_stream.append(f"({bp_escaped} ) Tj")
                self.current_stream.append("/F1 10 Tf")
                self.current_stream.append("0.25 0.25 0.25 rg")
                self.current_stream.append(f"({line_escaped}) Tj")
            else:
                self.current_stream.append("/F1 10 Tf")
                self.current_stream.append("0.25 0.25 0.25 rg")
                indent = 15 if bold_prefix and i > 0 else 0
                self.current_stream.append(f"1 0 0 1 {self.margin_x + indent} {self.y} Tm")
                self.current_stream.append(f"({line_escaped}) Tj")
            self.current_stream.append("ET")
            self.y -= 14
        self.y -= 4

    def add_bullet(self, text, bold_title=""):
        self.add_paragraph(text, bold_prefix=f"-  {bold_title}".strip())

    def add_code_block(self, lines_list):
        needed = len(lines_list) * 14 + 18
        self.check_space(needed)
        
        box_top = self.y
        box_height = len(lines_list) * 14 + 12
        box_y = box_top - box_height
        
        # Background box
        self.current_stream.append("0.96 0.97 0.98 rg") # light gray/blue fill
        self.current_stream.append(f"{self.margin_x} {box_y} {self.usable_width} {box_height} re f")
        # Border
        self.current_stream.append("0.85 0.88 0.92 RG 0.8 w")
        self.current_stream.append(f"{self.margin_x} {box_y} {self.usable_width} {box_height} re S")
        
        # Left accent border
        self.current_stream.append("0.15 0.45 0.75 rg")
        self.current_stream.append(f"{self.margin_x} {box_y} 3 {box_height} re f")
        
        text_y = box_top - 14
        for line in lines_list:
            escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            self.current_stream.append("BT")
            if line.strip().startswith("#"):
                self.current_stream.append("/F3 9.5 Tf 0.5 0.55 0.6 rg") # comment
            else:
                self.current_stream.append("/F4 9.5 Tf 0.1 0.15 0.2 rg") # code
            self.current_stream.append(f"1 0 0 1 {self.margin_x + 12} {text_y} Tm")
            self.current_stream.append(f"({escaped}) Tj")
            self.current_stream.append("ET")
            text_y -= 14
            
        self.y = box_y - 12

    def build(self, output_path):
        if self.current_stream:
            self._end_page()
            
        objects = []
        def add_obj(data):
            objects.append(data)
            return len(objects)

        # 1: Catalog
        # 2: Pages
        # 3.. Fonts
        # Page objects & content streams
        num_pages = len(self.pages)
        
        # Reserve obj IDs
        catalog_id = 1
        pages_id = 2
        f1_id = 3
        f2_id = 4
        f3_id = 5
        f4_id = 6
        
        next_id = 7
        page_obj_ids = []
        content_obj_ids = []
        for i in range(num_pages):
            page_obj_ids.append(next_id)
            content_obj_ids.append(next_id + 1)
            next_id += 2
            
        # Write PDF content
        out = bytearray()
        out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        
        offsets = {}
        
        def write_obj(num, body):
            offsets[num] = len(out)
            out.extend(f"{num} 0 obj\n".encode('latin1'))
            if isinstance(body, str):
                out.extend(body.encode('latin1'))
            else:
                out.extend(body)
            out.extend(b"\nendobj\n")

        # Catalog
        write_obj(catalog_id, f"<< /Type /Catalog /Pages {pages_id} 0 R >>")
        
        # Pages
        kids_str = " ".join([f"{pid} 0 R" for pid in page_obj_ids])
        write_obj(pages_id, f"<< /Type /Pages /Kids [{kids_str}] /Count {num_pages} >>")
        
        # Fonts
        write_obj(f1_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        write_obj(f2_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        write_obj(f3_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>")
        write_obj(f4_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>")
        
        # Pages & Contents
        for i in range(num_pages):
            pid = page_obj_ids[i]
            cid = content_obj_ids[i]
            stream = self.pages[i]
            
            p_dict = (
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {self.width} {self.height}] "
                f"/Contents {cid} 0 R "
                f"/Resources << /Font << /F1 {f1_id} 0 R /F2 {f2_id} 0 R /F3 {f3_id} 0 R /F4 {f4_id} 0 R >> >> >>"
            )
            write_obj(pid, p_dict)
            
            c_body = f"<< /Length {len(stream)} >>\nstream\n".encode('latin1') + stream + b"\nendstream"
            write_obj(cid, c_body)
            
        # Xref
        xref_offset = len(out)
        total_objs = next_id
        out.extend(f"xref\n0 {total_objs}\n0000000000 65535 f \n".encode('latin1'))
        for num in range(1, total_objs):
            off = offsets[num]
            out.extend(f"{off:010d} 00000 n \n".encode('latin1'))
            
        # Trailer
        out.extend(
            f"trailer\n<< /Size {total_objs} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n".encode('latin1')
        )
        
        with open(output_path, 'wb') as f:
            f.write(out)
        print(f"Generated {output_path} successfully ({len(self.pages)} pages).")

def main():
    pdf = PDFWriter()
    pdf._start_page()
    
    # Header
    pdf.add_title("GitHub Multi-Account Setup & Management Guide", "Personal Account Isolation (AntiGravity) vs. Company Account (VS Code)")
    
    pdf.add_paragraph("This guide details how your Mac is configured to seamlessly run both your Company GitHub account (in VS Code) and your Personal GitHub account (in Google AntiGravity) without any cross-account conflicts or risk of leaking credentials.")
    
    pdf.add_section_header("1. Core Concept & Isolation Architecture")
    pdf.add_bullet("Company work remains untouched in VS Code and uses your company credentials stored in macOS Keychain.", "Work Isolation:")
    pdf.add_bullet("All projects inside ~/Documents/Google_AntiGravity/ automatically use your personal identity and personal SSH key.", "Personal Isolation:")
    pdf.add_bullet("Personal author identity is locked to shoaibmumtaz <shoaibmumtaz28@gmail.com>.", "Author Identity:")
    pdf.add_bullet("Even if you paste an HTTPS GitHub link, Git translates it to SSH so macOS Keychain never tries to log in with your company account.", "URL Translation:")

    pdf.add_section_header("2. Active Configuration Summary")
    pdf.add_bullet("~/.ssh/id_ed25519_personal (Added to GitHub account: shoaibmumtaz)", "Dedicated SSH Key:")
    pdf.add_bullet("~/.gitconfig contains includeIf for ~/Documents/Google_AntiGravity/", "Global Git Rule:")
    pdf.add_bullet("~/.gitconfig-antigravity contains user details, SSH command, and URL rules.", "Dedicated Config:")
    pdf.add_bullet("./backup.sh script keeps versioned local zips and bundle snapshots in _Backups/.", "Local Backup System:")

    pdf.add_section_header("3. Step-by-Step: Connecting a Project to GitHub")
    pdf.add_paragraph("When you create a new repository on github.com (under shoaibmumtaz) and want to link it:")
    pdf.add_code_block([
        "# 1. Add your repository remote URL (HTTPS or SSH both work):",
        "git remote add origin https://github.com/shoaibmumtaz/my-repo.git",
        "",
        "# 2. Push your main branch to GitHub:",
        "git push -u origin main"
    ])

    pdf.add_section_header("4. Step-by-Step: Verifying Current Account & Remotes")
    pdf.add_paragraph("To check which identity and remote any repository is currently configured with:")
    pdf.add_code_block([
        "# Check commit author name & email:",
        "git config user.name",
        "git config user.email",
        "",
        "# Check where the repository pushes to:",
        "git remote -v"
    ])

    pdf.add_section_header("5. Step-by-Step: Changing Settings for a Single Project")
    pdf.add_paragraph("If you ever need to override the name, email, or remote for just one project:")
    pdf.add_code_block([
        "# Set a custom author name or email for ONLY this repository:",
        'git config user.name "Your Name"',
        'git config user.email "your-email@example.com"',
        "",
        "# Change the remote GitHub repository URL:",
        "git remote set-url origin https://github.com/shoaibmumtaz/new-repo.git",
        "",
        "# Disconnect from GitHub entirely (reverts to local-only):",
        "git remote remove origin"
    ])

    pdf.add_section_header("6. Step-by-Step: Managing or Modifying the Automatic Rule")
    pdf.add_paragraph("Your personal settings are stored cleanly in dedicated config files:")
    pdf.add_code_block([
        "# View your active global Git settings:",
        "git config --global --list",
        "",
        "# Edit your personal AntiGravity settings (email, key, etc.):",
        "nano ~/.gitconfig-antigravity",
        "",
        "# To disable the automatic folder rule completely in the future:",
        'git config --global --unset "includeIf.gitdir:~/Documents/Google_AntiGravity/.path"'
    ])

    pdf.add_section_header("7. Local Backup Workflow Reminder")
    pdf.add_paragraph("As defined in the project version control rules, local snapshots are created using:")
    pdf.add_code_block([
        './backup.sh "Describe what was changed"    # Creates local commit, tag & zip',
        './backup.sh list                          # Displays all timestamped backups'
    ])

    out_file = "/Users/shoaib/Documents/Google_AntiGravity/01_AntiGravity_Test/Main/Git_Account_Setup_Guide.pdf"
    pdf.build(out_file)

if __name__ == "__main__":
    main()