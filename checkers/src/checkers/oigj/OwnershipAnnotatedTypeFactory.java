package checkers.oigj;

import javax.lang.model.element.ElementKind;

import com.sun.source.tree.CompilationUnitTree;

import javacutils.TypesUtils;

import checkers.oigj.quals.*;
import checkers.types.BasicAnnotatedTypeFactory;
import checkers.types.TypeAnnotator;
import checkers.types.AnnotatedTypeMirror.AnnotatedDeclaredType;

public class OwnershipAnnotatedTypeFactory extends BasicAnnotatedTypeFactory<OwnershipSubchecker> {

    public OwnershipAnnotatedTypeFactory(OwnershipSubchecker checker,
            CompilationUnitTree root) {
        super(checker, root);
        this.postInit();
    }


    @Override
    protected TypeAnnotator createTypeAnnotator(OwnershipSubchecker checker) {
        return new OwnershipTypeAnnotator(checker);
    }

    private class OwnershipTypeAnnotator extends TypeAnnotator {

        public OwnershipTypeAnnotator(OwnershipSubchecker checker) {
            super(checker, OwnershipAnnotatedTypeFactory.this);
        }

        public Void visitDeclared(AnnotatedDeclaredType type, ElementKind p) {
            if (type.isAnnotated())
                return super.visitDeclared(type, p);

            if (p == ElementKind.CLASS && TypesUtils.isObject(type.getUnderlyingType()))
                type.addAnnotation(World.class);
            return super.visitDeclared(type, p);
        }
    }
}